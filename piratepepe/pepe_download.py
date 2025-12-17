"""Pepe asset downloading functions."""

import contextlib
import time
from pathlib import Path

import requests
from colorama import Back, Fore, Style
from tqdm import tqdm
from urllib3.exceptions import ReadTimeoutError

from . import skipped_files
from .config import config
from .constants import FUN_TQDM_LOADING_BAR
from .helpers import check_file
from .ipfs_gateways import gateway_handler


def download_pepe_asset(stripped_url: str, file_name: str) -> bool:
    """Try all gateways to download asset."""
    file_path = Path(config.output_folder) / file_name

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
                file_path.open("wb") as f,
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
                file_path.unlink()
            return (False, "FileWrongFormat")

        print(f"{Back.WHITE}{Fore.GREEN} Success! {Style.RESET_ALL}")
        return (True, None)

    return gateway_handler.try_gateways(try_download)


def download_pepe(url: str, file_name: str) -> bool:
    """Download the asset, hardcoded to output."""
    file_downloaded = False
    file_path = Path(config.output_folder) / file_name

    # the nft json for this collection has the ipfs.io gateway hardcoded in lmao, maybe this is normal 🤷
    stripped_url = url.replace("https://ipfs.io/ipfs/", "")

    # In theory this one should always work, chainsaw nfs should be hosting the assets...
    chainsaw_gateway = "https://chainsaw.mypinata.cloud/ipfs/"

    gateway_handler.add_gateway(chainsaw_gateway)

    if not file_path.is_file():  # This is where the magic happens
        file_downloaded = download_pepe_asset(stripped_url, file_name)
    else:
        print(f"Already downloaded: {file_name}")
        file_downloaded = True

    if not file_downloaded:
        skipped_files.add_skipped_file(file_name)

    return file_downloaded
