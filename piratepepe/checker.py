"""Check media files for incorrect content types and integrity issues."""

import contextlib
from pathlib import Path

import ffmpeg
import magic

from .logger import get_logger

logger = get_logger(__name__)

MIME_MAP = {
    ".gif": ["image/gif"],
    ".glb": ["application/octet-stream"],
    ".png": ["image/png", "image/jpeg"],  # Well done idiots.
    ".mp4": ["video/mp4"],
    ".json": ["application/json"],
}

AV_EXTENSIONS = [".mp4", ".gif"]

FFMPEG_AVAILABLE = False
with contextlib.suppress(FileNotFoundError):
    ffmpeg.input("testsrc=duration=0.5:size=16x16:rate=1", f="lavfi").output(filename="-", f="null").run(
        quiet=True, capture_stderr=True
    )
    FFMPEG_AVAILABLE = True


def _check_file_type(file_path: Path) -> bool:
    """Check if file has correct content type using python-magic."""
    mime = magic.from_file(str(file_path), mime=True)

    expected_mime = MIME_MAP.get(file_path.suffix.lower())
    if expected_mime is None:
        logger.error("Unknown file extension: %s", file_path.suffix)
        return False

    if mime not in expected_mime:
        msg = f"MIME type mismatch for file {file_path.name}\nExpected MIME: {expected_mime}, Detected MIME: {mime}"
        logger.error(msg)
        return False

    logger.debug(" MIME Pass!")
    return True


def _check_av_file_with_ffmpeg(file_path: Path) -> bool:
    """Check AV file integrity using ffmpeg."""
    if not FFMPEG_AVAILABLE:
        msg = (
            "FFMPEG not available, skipping AV file integrity check."
            "\n"
            "You should really install it since the files are often corrupted."
        )
        logger.warning(msg)
        return True

    try:
        ff_output = ffmpeg.input(file_path).output(filename="-", f="null").run(quiet=True, capture_stderr=True)
    except ffmpeg.exceptions.FFMpegError as e:
        logger.error(" FFMPEG Error: %s", e.stderr.decode().strip())  # noqa: TRY400
        logger.error(ff_output.stderr.decode().strip())  # noqa: TRY400
        return False

    logger.debug(" FFMPEG Pass!")
    return True


def check_file(file_path: Path) -> bool:
    """Check a single file for content type and integrity issues."""
    will_check_av = file_path.suffix.lower() in AV_EXTENSIONS

    if will_check_av:
        logger.debug(" Checking AV file: %s", file_path.name)
    else:
        logger.debug(" Checking file: %s", file_path.name)

    if not _check_file_type(file_path):
        return False

    result = not (will_check_av and not _check_av_file_with_ffmpeg(file_path))
    if result:
        logger.debug("File check passed: %s", file_path.name)

    return result
