"""Json handling."""

import json
import time

import requests
from pydantic import ValidationError
from requests.exceptions import RequestException

from .config import config
from .helpers import summarize_validation_error
from .ipfs_gateways import gateway_handler
from .logger import get_logger
from .models import PepeNFT

logger = get_logger(__name__)


def _load_existing_json(pepe_ipfs: str) -> PepeNFT | None:
    """Check if JSON already exists on disk and load it."""
    output_dir = config.output_folder
    for filepath in output_dir.glob("*.json"):
        if pepe_ipfs in filepath.name:
            logger.debug("JSON already exists at %s, loading from disk.", filepath)
            try:
                json_data = json.loads(filepath.read_text())
                return PepeNFT(**json_data)
            except ValidationError as e:
                summarize_validation_error(f"existing JSON at {filepath}:", e)
                break
    return None


def _fetch_json_from_url(url: str) -> dict:
    """Fetch and parse JSON from a URL."""
    response = requests.get(url, headers=config.headers, timeout=config.http_timeout)

    if not response:
        msg = f"Empty response from {url}"
        raise RequestException(msg)

    if not response.ok:
        msg = f"Bad response ({response.status_code}) from {url}"
        raise RequestException(msg)

    return response.json()


def _create_gateway_callback(pepe_ipfs: str) -> tuple[callable, list]:
    """Create a callback function for gateway attempts and a container for results."""
    result_container = [None]  # Use list to allow mutation in nested function

    def try_fetch_json(gateway: str) -> tuple[bool, str | None]:
        """Try fetching JSON from a single gateway."""
        if config.slow_mode:
            logger.info("Waiting a minute before downloading")
            time.sleep(61)

        url = gateway + pepe_ipfs
        logger.info("Trying: %s", url)

        try:
            json_data = _fetch_json_from_url(url)
            pepe_nft = PepeNFT(**json_data)
            result_container[0] = pepe_nft

        except (RequestException, KeyError) as e:
            return (False, type(e).__name__)
        except ValidationError as e:
            summarize_validation_error(f"JSON from {url}:", e)
            return (False, "ValidationError")

        return (True, None)

    return try_fetch_json, result_container


def grab_pepe_json(pepe_ipfs: str) -> PepeNFT | None:
    """Fetch Pepe NFT JSON data from IPFS, trying multiple gateways if needed."""
    # First, check if we already have this JSON on disk
    existing_pepe = _load_existing_json(pepe_ipfs)
    if existing_pepe:
        return existing_pepe

    # Try to fetch from IPFS gateways
    callback, result_container = _create_gateway_callback(pepe_ipfs)
    success = gateway_handler.try_gateways(callback)

    if not success:
        logger.info("All gateways failed getting the json...")
        return None

    return result_container[0]
