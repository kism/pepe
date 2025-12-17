"""pepe.py main."""

import argparse
import json
import sys
from pathlib import Path

from colorama import Back, Fore, Style

from . import skipped_files
from .config import config
from .helpers import print_debug, scan_pepe_file
from .ipfs_gateways import gateway_handler
from .models import PepeNFT
from .pepe_download import download_pepe
from .pepe_json import grab_pepe_json


def process_pepe_nft_json(pepe_nft: PepeNFT, pepe_ipfs: str) -> None:
    """Process the json for the toke, call the download functions."""
    nftjson = json.dumps(pepe_nft.model_dump(), indent=2)
    output_dir = Path(config.output_folder)
    output_dir.mkdir(exist_ok=True)

    # Save the json file of the nft, this might be what's considered the ipfs object metadata
    old_json_file = output_dir / f"{pepe_nft.name}.json"
    if old_json_file.exists():
        old_json_file.unlink()

    json_file = output_dir / f"{pepe_nft.name}.{pepe_ipfs}.json"
    json_file.write_text(nftjson)

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
            process_pepe_nft_json(pepe_nft, pepe_ipfs)
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
    parser.add_argument("-o", "--output", type=Path, default="output", help="Output folder")
    args = parser.parse_args()

    config.debug = args.debug
    config.output_folder = args.output
    config.start_point = args.start - 1
    config.slow_mode = args.slow
    config.validate()

    try:
        main()
    except KeyboardInterrupt:
        print()
        print("🙋‍♀️ Bye")
