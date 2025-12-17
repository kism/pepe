"""Json handling."""

import json
import time

import requests
from pydantic import ValidationError
from requests.exceptions import RequestException

from .config import config
from .helpers import print_debug, summarize_validation_error
from .ipfs_gateways import gateway_handler
from .models import PepeNFT


def grab_pepe_json(pepe_ipfs: str) -> PepeNFT | None:
    """Iterate through gateways to get Pepe's json."""  # since they probably suck
    # Check if JSON already exists on disk
    output_dir = config.output_folder
    for filepath in output_dir.glob("*.json"):
        if pepe_ipfs in filepath.name:
            print(f"JSON for {pepe_ipfs} already exists at {filepath}, loading from disk.")
            json_data = json.loads(filepath.read_text())
            try:
                return PepeNFT(**json_data)
            except ValidationError as e:
                summarize_validation_error(f"existing JSON at {filepath}:", e)
                break

    pepe_nft: PepeNFT | None = None

    def try_fetch_json(gateway: str) -> tuple[bool, str | None]:
        """Try fetching JSON from a single gateway."""
        nonlocal pepe_nft

        if config.slow_mode:
            print("Waiting a minute before downloading")
            time.sleep(61)

        request = gateway + pepe_ipfs
        print(f"Trying: {request}")

        try:
            response = requests.get(request, headers=config.headers, timeout=config.http_timeout)

            if not response:
                return (False, "None")

            if not response.ok:
                return (False, f"HTTP {response.status_code}")

            json_data = response.json()

            pepe_nft = PepeNFT(**json_data)

        except RequestException as e:
            return (False, type(e).__name__)
        except KeyError as e:
            return (False, type(e).__name__)
        except ValidationError as e:
            summarize_validation_error(f"JSON from {request}:", e)
            return (False, "ValidationError")

        return (True, None)

    success = gateway_handler.try_gateways(try_fetch_json)

    if not success:
        print("All gateways failed getting the json...")

    return pepe_nft
