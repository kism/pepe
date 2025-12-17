#!/usr/bin/env python3
"""pepe.py main."""

import argparse
import contextlib
import json
import os
import sys
import time

import magic
import requests
from colorama import Back, Fore, Style
from requests.exceptions import RequestException
from tqdm import tqdm
from urllib3.exceptions import ReadTimeoutError

from . import skipped_files
from .config import config
from .constants import FUN_TQDM_LOADING_BAR, IPFS_GATEWAY_LIST, PEPES_TXT
from .ipfs_gateways import IPFSGatewayHandler
from .models import HifiMedia, PepeNFT

gateway_handler = IPFSGatewayHandler(IPFS_GATEWAY_LIST)


def print_debug(text: str) -> None:
    """Debug messages in yellow if the debug global is true."""
    if config.debug:
        print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")


def scan_pepe_file(start_point: int) -> list[str]:
    """Scan pepe_txt var for ipfs links."""
    pepe_list_str = PEPES_TXT

    listfresh: list[str] = []
    for element in pepe_list_str.split():
        # Ignore everything that doesn't start with a Q since that's what all them things seem to start with
        if element[0] == "Q":
            listfresh.append(element.strip())
        else:
            print_debug(f"Not a pepe: {element.strip()}")
    pepe_list = listfresh
    print_debug(f"Pepe list: [{pepe_list!s}")

    print(f"Found {len(pepe_list)} tokenURIs to look for Pepe")

    if start_point > -1:
        pepe_list = pepe_list[start_point:]
        print(f"Trimming first {start_point} tokenURIs in list")

    return pepe_list


def check_file(file_path: str) -> bool:
    """Check if a file is heck."""
    mime = magic.Magic(mime=True, uncompress=True)

    try:
        file_type = mime.from_file(file_path)
        print(f"Found file type: {file_type}")
        return file_type.startswith("text")
    except FileNotFoundError:
        return False


def download_pepe_asset(stripped_url: str, file_name: str) -> bool:
    """Try all gateways to download asset."""
    file_path = config.output_folder + os.sep + file_name

    def try_download(gateway: str) -> tuple[bool, str | None]:
        """Try downloading from a single gateway."""
        if config.slow_mode:
            print("Waiting a minute before downloading")
            time.sleep(60)

        url = gateway + stripped_url
        print(f"Attempting to download Pepe NFT Asset: '{file_name}' from: {url}")

        try:
            with (
                requests.get(url, stream=True, headers=config.headers, timeout=config.http_timeout * 2) as r,
                open(file_path, "wb") as f,
            ):
                total_size = int(r.headers.get("content-length", 0))
                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    leave=False,
                    ascii=FUN_TQDM_LOADING_BAR,
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, ReadTimeoutError) as e:
            print()
            error_name = type(e).__name__
            if isinstance(e, requests.exceptions.ConnectionError):
                print(f"{Fore.RED}Download Failed{Style.RESET_ALL}")
                if url.endswith("mp4"):
                    print("gateway might not have large file support")
            else:
                print(f"Timeout of {config.http_timeout} seconds reached")
            return (False, error_name)

        # Check if file is valid
        if check_file(file_path):
            print("Gateway didn't give us the file correctly, removing file if it exists")
            with contextlib.suppress(FileNotFoundError):
                os.remove(file_path)
            return (False, "FileWrongFormat")

        print(f"{Back.WHITE}{Fore.GREEN} Success! {Style.RESET_ALL}")
        return (True, None)

    return gateway_handler.try_gateways(try_download)


def download_pepe(url: str, file_name: str) -> bool:
    """Download the asset, hardcoded to output."""
    file_downloaded = False
    file_path = config.output_folder + os.sep + file_name

    # the nft json for this collection has the ipfs.io gateway hardcoded in lmao, maybe this is normal 🤷
    stripped_url = url.replace("https://ipfs.io/ipfs/", "")

    # In theory this one should always work, chainsaw nfs should be hosting the assets...
    chainsaw_gateway = "https://chainsaw.mypinata.cloud/ipfs/"

    gateway_handler.add_gateway(chainsaw_gateway)

    if not os.path.isfile(file_path):  # This is where the magic happens
        file_downloaded = download_pepe_asset(stripped_url, file_name)
    else:
        print(f"Already downloaded: {file_name}")
        file_downloaded = True

    if not file_downloaded:
        skipped_files.add_skipped_file(file_name)

    return file_downloaded


def process_pepe_nft_json(pepe_nft: PepeNFT) -> None:
    """Process the json for the toke, call the download functions."""
    # No idea why python json uses a single quote
    import json

    nftjson = json.dumps(
        {
            "name": pepe_nft.name,
            "image": pepe_nft.image,
            "animation_url": pepe_nft.animation_url,
            "hifi_media": {
                "video": pepe_nft.hifi_media.video,
                "card_front": pepe_nft.hifi_media.card_front,
                "card_back": pepe_nft.hifi_media.card_back,
            },
            "pepe_ipfs": pepe_nft.pepe_ipfs,
        },
        indent=2,
    )
    with contextlib.suppress(FileExistsError):
        os.mkdir(config.output_folder)

    # Save the json file of the nft, this might be whats considered the ipfs object metadata
    with open(config.output_folder + "/" + pepe_nft.name + ".json", "w") as nftjsonfile:
        nftjsonfile.write(nftjson)

    # Download all the things from the json, these are ipfs links
    download_pepe(pepe_nft.image, pepe_nft.name + " - " + "card.gif")
    download_pepe(pepe_nft.animation_url, pepe_nft.name + " - " + "card.glb")

    if pepe_nft.hifi_media.card_front:
        download_pepe(
            pepe_nft.hifi_media.card_front,
            pepe_nft.name + " - " + "front.png",
        )
    else:
        print("No 'card_front', this is the case with some of the Sparklers.")

    if pepe_nft.hifi_media.card_back:
        download_pepe(
            pepe_nft.hifi_media.card_back,
            pepe_nft.name + " - " + "back.png",
        )
    else:
        print("No 'card_back', this is the case with the Sparklers.")

    download_pepe(pepe_nft.hifi_media.video, pepe_nft.name + " - " + "video.mp4")


def grab_pepe_json(pepe_ipfs: str) -> PepeNFT | None:
    """Iterate through gateways to get Pepe's json."""  # since they probably suck

    # Check if JSON already exists on disk
    if os.path.isdir(config.output_folder):
        for filename in os.listdir(config.output_folder):
            if filename.endswith(".json"):
                filepath = os.path.join(config.output_folder, filename)
                try:
                    with open(filepath, "r") as f:
                        json_data = json.load(f)
                        if json_data.get("pepe_ipfs") == pepe_ipfs:
                            print(f"Found existing JSON on disk: {filename}")
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
                    print_debug(f"Error reading {filename}: {e}")
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


def process_pepes(pepe_list: list[str]) -> None:
    """Iterate through the pepes."""
    for pepe_ipfs in pepe_list:
        print()
        print(
            f"{Back.WHITE}{Fore.BLACK} Looking for {Fore.GREEN}Pepe{Fore.BLACK} and his NFT json... {Style.RESET_ALL}",
        )

        pepe_nft = grab_pepe_json(pepe_ipfs)

        if pepe_nft:
            print(f"Found a Rare Pepe! : {pepe_nft.name}")
            process_pepe_nft_json(pepe_nft)
        else:
            print(f"{Fore.RED}All is heck{Style.RESET_ALL} every defined ipfs gateway sucks")
            skipped_files.add_skipped_file("Entire Pepe Json: " + pepe_ipfs)


def main() -> None:
    """Main."""
    exitcode = 1
    print(f"{Back.WHITE}{Fore.BLACK} pirate{Fore.GREEN}pepe {Fore.BLACK}.py {Style.RESET_ALL}")
    print_debug("Debug on!\n")

    pepe_list = scan_pepe_file(config.start_point)

    try:
        process_pepes(pepe_list)
    except KeyboardInterrupt:
        skipped_files.add_skipped_file("<Interrupted by user>")
        print("Exiting due to ^C")

    print(f"\n {Back.WHITE}{Fore.BLACK} Done! {Style.RESET_ALL}")

    gateway_handler.print_statistics()

    if skipped_files.has_skipped_files():
        print("Some Downloads failed")
        print()
        print(f"{Fore.RED}Missing Pepe Assets{Style.RESET_ALL}:")
        for file in skipped_files.get_skipped_files():
            print(f" {file}")
        print()
        print("Run the script again to try again.")
        print(
            "You might want to find some new ipfs gateways and add them to the script, "
            "or get a new IP address since some ipfs gateways will rate-limit or block you for downloading too much.",
        )
    else:
        print("All the Pepes should be downloaded!")
        exitcode = 0

    sys.exit(exitcode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matt Furie rarepepes.fun downloader")
    parser.add_argument("-d", "--debug", action="store_true", help="Increase output verbosity")
    parser.add_argument("--slow", action="store_true", help="Wait a minute before each download attempt")
    parser.add_argument("-s", "--start", type=int, default=0, help="n Pepe to start from")
    parser.add_argument("-o", "--output", type=str, default="output", help="Output folder")
    args = parser.parse_args()

    config.debug = args.debug
    config.output_folder = args.output
    config.start_point = args.start - 1
    config.slow_mode = args.slow

    try:
        main()
    except KeyboardInterrupt:
        print()
        print("🙋‍♀️ Bye")
