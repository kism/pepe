"""Check media files for incorrect content types and integrity issues."""

import subprocess
from pathlib import Path

import magic

MIME_MAP = {
    ".gif": "image/gif",
    ".glb": "application/octet-stream",
    ".png": "image/png",
    ".mp4": "video/mp4",
    ".json": "application/json",
}

AV_EXTENSIONS = [".mp4", ".gif"]


def _check_file_type(file_path: Path) -> bool:
    """Check if file has correct content type using python-magic."""
    print(f'FILE checking: "{file_path}"...')
    mime = magic.from_file(str(file_path), mime=True)

    expected_mime = MIME_MAP.get(file_path.suffix.lower())
    if expected_mime is None:
        print(f" Unknown file extension: {file_path.suffix}")
        return False

    if mime != expected_mime:
        print(f" Expected MIME: {expected_mime}, Detected MIME: {mime}")
        return False

    print(" MIME Pass!")
    return True


def _check_av_file_with_ffmpeg(file_path: Path) -> bool:
    """Check AV file integrity using ffmpeg."""
    print(f'FFMPEG checking: "{file_path}"...')

    try:
        # Use ffmpeg to validate the file
        # -v error: only show errors
        # -i: input file
        # -f null -: output to null (just validate, don't write)
        result = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(file_path), "-f", "null", "-"],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
    except (subprocess.SubprocessError, OSError) as e:
        print(f" Error checking file: {e}")
        print(f' Adding "{file_path}" to the borked file list')
        return False
    else:
        if result.returncode != 0:
            print(f' Adding "{file_path}" to the borked file list')
            return False

        print(" FFMPEG Pass!")
        return True


def _check_av_files(files: list[Path], existing_borked: list[Path]) -> list[Path]:
    """Check AV files with ffmpeg and return newly identified borked files."""
    return [
        file_path
        for file_path in files
        if not _check_av_file_with_ffmpeg(file_path) and file_path not in existing_borked
    ]


def check_file(file_path: Path) -> bool:
    """Check a single file for content type and integrity issues."""
    if not _check_file_type(file_path):
        return False

    return not (file_path.suffix.lower() in AV_EXTENSIONS and not _check_av_file_with_ffmpeg(file_path))
