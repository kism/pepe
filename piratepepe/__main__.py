"""pepe.py main."""

import argparse
import json
import sys
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.rule import Rule
from rich.traceback import install

from . import skipped_files
from .config import config
from .helpers import scan_pepe_file
from .ipfs_gateways import gateway_handler
from .logger import get_logger, setup_logger
from .models import PepeNFT
from .pepe_download import download_pepe
from .pepe_json import grab_pepe_json

install()
logger = get_logger(__name__)
setup_logger()


def process_pepe_nft_json(pepe_nft: PepeNFT, pepe_ipfs: str) -> None:
    """Process the json for the toke, call the download functions."""
    nftjson = json.dumps(pepe_nft.model_dump(), indent=2)
    output_dir = Path(config.output_folder)
    output_dir.mkdir(exist_ok=True)

    downloads: list[Literal["failed", "downloaded", "exists"]] = []

    # Save the json file of the nft, this might be what's considered the ipfs object metadata
    old_json_file = output_dir / f"{pepe_nft.name}.json"
    if old_json_file.exists():
        old_json_file.unlink()

    json_file = output_dir / f"{pepe_nft.name}.{pepe_ipfs}.json"
    json_file.write_text(nftjson)

    # Download all the things from the json, these are ipfs links
    downloads.append(download_pepe(pepe_nft.image, pepe_nft.name + " - " + "card.gif"))
    downloads.append(download_pepe(pepe_nft.animation_url, pepe_nft.name + " - " + "card.glb"))

    if pepe_nft.hifi_media.card_front:
        downloads.append(
            download_pepe(
                pepe_nft.hifi_media.card_front,
                pepe_nft.name + " - " + "front.png",
            )
        )
    else:
        logger.info("No 'card_front', this is the case with some of the Sparklers.")

    if pepe_nft.hifi_media.card_back:
        downloads.append(
            download_pepe(
                pepe_nft.hifi_media.card_back,
                pepe_nft.name + " - " + "back.png",
            )
        )
    else:
        logger.info("No 'card_back', this is the case with the Sparklers.")

    downloads.append(download_pepe(pepe_nft.hifi_media.video, pepe_nft.name + " - " + "video.mp4"))

    success_count = sum(1 for d in downloads if d == "downloaded")
    exists_count = sum(1 for d in downloads if d == "exists")
    skipped_count = sum(1 for d in downloads if d == "failed")
    total_count = len(downloads)

    if success_count + exists_count == len(downloads):
        if exists_count == total_count:
            msg = f"{exists_count}/{total_count} files already exist, nothing new downloaded."
        elif exists_count == 0:
            msg = f"{success_count}/{total_count} files downloaded successfully!"
        else:
            msg = f"{success_count}/{total_count} files downloaded, {exists_count}/{total_count} files already exist."
        logger.info(msg)
    else:
        if exists_count == 0:
            msg = f"{skipped_count}/{total_count} files failed to download."
        else:
            msg = f"{skipped_count}/{total_count} files failed to download, {exists_count}/{total_count} files already exist."  # noqa: E501
        logger.error(msg)


def process_pepes(pepe_list: list[str]) -> None:
    """Iterate through the pepes."""
    console = Console()

    for pepe_ipfs in pepe_list:
        console.print(Rule(style="green"))
        logger.info("Looking for Pepe and his NFT json...")

        pepe_nft = grab_pepe_json(pepe_ipfs)

        if pepe_nft:
            logger.info("Found a Rare Pepe! : %s", pepe_nft.name)
            process_pepe_nft_json(pepe_nft, pepe_ipfs)
        else:
            logger.error("All is heck every defined ipfs gateway sucks")
            skipped_files.add_skipped_file("Entire Pepe Json: " + pepe_ipfs)


def main() -> None:
    """Main."""
    exitcode = 1
    logger.info("piratepepe.py")
    logger.debug("Debug on!\n")

    pepe_list = scan_pepe_file()

    try:
        process_pepes(pepe_list)
    except KeyboardInterrupt:
        skipped_files.add_skipped_file("<Interrupted by user>")
        logger.info("Exiting due to ^C")

    logger.info("Done!")

    gateway_handler.print_statistics()

    if not skipped_files.has_skipped_files():
        logger.info("All the Pepes should be downloaded!")
        exitcode = 0

    sys.exit(exitcode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matt Furie rarepepes.fun downloader")
    parser.add_argument("--slow", action="store_true", help="Wait a minute before each download attempt")
    parser.add_argument("-o", "--output", type=Path, default="output", help="Output folder")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity level (can be used multiple times)"
    )
    args = parser.parse_args()
    setup_logger(verbosity=args.verbose)

    config.output_folder = args.output
    config.slow_mode = args.slow
    config.validate()

    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bye")
