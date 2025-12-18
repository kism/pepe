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


def grab_pepe_json(pepe_ipfs: str) -> PepeNFT | None:
    """Fetch Pepe NFT JSON data from IPFS, trying multiple gateways if needed."""
    # First, check if we already have this JSON on disk
    existing_pepe = _load_existing_json(pepe_ipfs)
    if existing_pepe:
        return existing_pepe

    # Try to fetch from IPFS gateways
    for gateway in gateway_handler.iterate_gateways():
        if config.slow_mode:
            logger.info("Waiting a minute before downloading")
            time.sleep(61)

        url = gateway.url + pepe_ipfs
        logger.info("Trying: %s", url)

        try:
            response = requests.get(url, headers=config.headers, timeout=config.http_timeout)
            json_data = response.json()
            pepe_nft = PepeNFT(**json_data)
        except (RequestException, KeyError) as e:
            gateway.report_failure(type(e).__name__)
        except ValidationError as e:
            summarize_validation_error(f"JSON from {url}:", e)
            gateway.report_failure("ValidationError")
        except Exception as e:  # noqa: BLE001
            gateway.report_failure(type(e).__name__)
        else:
            gateway.report_success()
            return pepe_nft

    logger.info("All gateways failed getting the json...")
    return None
