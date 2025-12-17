"""Json handling."""

import json
import time

import requests
from requests.exceptions import RequestException

from .config import config
from .helpers import print_debug
from .ipfs_gateways import gateway_handler
from .models import HifiMedia, PepeNFT


def grab_pepe_json(pepe_ipfs: str) -> PepeNFT | None:
    """Iterate through gateways to get Pepe's json."""  # since they probably suck
    # Check if JSON already exists on disk
    output_dir = config.output_folder
    for filepath in output_dir.glob("*.json"):
        try:
            json_data = json.loads(filepath.read_text())
            if json_data.get("pepe_ipfs") == pepe_ipfs:
                print(f"Found existing JSON on disk: {filepath.name}")
                hifi_media = HifiMedia(
                    video=json_data["hifi_media"]["video"],
                    card_front=json_data["hifi_media"].get("card_front"),
                    card_back=json_data["hifi_media"].get("card_back"),
                )
                return PepeNFT(
                    name=json_data["name"],
                    image=json_data["image"],
                    animation_url=json_data["animation_url"],
                    hifi_media=hifi_media,
                    pepe_ipfs=pepe_ipfs,
                )
        except (json.JSONDecodeError, KeyError) as e:
            print_debug(f"Error reading {filepath.name}: {e}")
            continue

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
            # Construct the dataclass from the JSON response
            hifi_media = HifiMedia(
                video=json_data["hifi_media"]["video"],
                card_front=json_data["hifi_media"].get("card_front"),
                card_back=json_data["hifi_media"].get("card_back"),
            )
            pepe_nft = PepeNFT(
                name=json_data["name"],
                image=json_data["image"],
                animation_url=json_data["animation_url"],
                hifi_media=hifi_media,
                pepe_ipfs=pepe_ipfs,
            )

        except RequestException as e:
            return (False, type(e).__name__)
        except KeyError as e:
            return (False, type(e).__name__)

        return (True, None)

    success = gateway_handler.try_gateways(try_fetch_json)

    if not success:
        print("All gateways failed getting the json...")

    return pepe_nft
