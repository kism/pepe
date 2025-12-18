"""Pepe asset downloading functions."""

import contextlib
import time
import warnings
from pathlib import Path
from typing import Literal

import requests
from requests import RequestException
from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm
from urllib3.exceptions import ReadTimeoutError

from . import skipped_files
from .checker import check_file
from .config import config
from .ipfs_gateways import gateway_handler
from .logger import get_logger

warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)

logger = get_logger(__name__)


def download_pepe_asset(stripped_url: str, file_name: str) -> bool:
    """Try all gateways to download asset."""
    file_path = Path(config.output_folder) / file_name

    for gateway in gateway_handler.iterate_gateways():
        if config.slow_mode:
            logger.info("Waiting a minute before downloading")
            time.sleep(60)

        url = gateway.url + stripped_url
        logger.info("Attempting to download Pepe NFT Asset: '%s' from: %s", file_name, url)

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
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
        except (RequestException, ReadTimeoutError) as e:
            error_name = type(e).__name__

            if isinstance(e, requests.exceptions.ConnectionError) and url.endswith("mp4"):
                logger.warning("Download Failed: Gateway might not have large file support")
            else:
                logger.warning("Download Failed: %s", error_name)

            gateway.report_failure(error_name)
            continue

        # Check if file is valid
        if not check_file(file_path):
            logger.warning("Gateway didn't give us the file correctly, removing file if it exists")
            with contextlib.suppress(FileNotFoundError):
                file_path.unlink()
            gateway.report_failure("FileWrongFormat")
            continue

        logger.debug("Download Complete, file not checked yet.")
        gateway.report_success()
        return True

    return False


def download_pepe(url: str, file_name: str) -> Literal["downloaded", "failed", "exists"]:
    """Download the asset, hardcoded to output."""
    file_status: Literal["downloaded", "failed", "exists"] = "failed"

    file_downloaded = False
    file_path = Path(config.output_folder) / file_name

    # Check the existing file if it exists
    if file_path.is_file():
        check_file_ok = check_file(file_path)
        if not check_file_ok:
            with contextlib.suppress(FileNotFoundError):
                file_path.unlink()

    # the nft json for this collection has the ipfs.io gateway hardcoded in lmao, maybe this is normal 🤷
    stripped_url = url.replace("https://ipfs.io/ipfs/", "")

    if not file_path.is_file():  # This is where the magic happens
        file_downloaded = download_pepe_asset(stripped_url, file_name)
        file_status = "downloaded" if file_downloaded else "failed"
    else:
        logger.debug("Already downloaded: %s", file_name)
        file_status = "exists"

    if file_status == "failed":
        skipped_files.add_skipped_file(file_name)
    if file_status == "downloaded":
        logger.info("Successfully downloaded: %s", file_name)

    return file_status
