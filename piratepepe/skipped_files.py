"""Track files that failed to download."""

from .logger import get_logger

logger = get_logger(__name__)
files_skipped: list[str] = []


SPIEL = """
Run the script again to try again.
You might want to find some new ipfs gateways and add them to the script,
or get a new IP address since some ipfs gateways will rate-limit or block you for downloading too much.
"""


def add_skipped_file(filename: str) -> None:
    """Add a file to the skipped files list."""
    files_skipped.append(filename)


def has_skipped_files() -> bool:
    """Check if any files were skipped."""
    if len(files_skipped) > 0:
        lines = [
            "Some Downloads failed",
            "Missing Pepe Assets",
        ]
        lines.extend([f" {file}" for file in get_skipped_files()])
        lines.extend([SPIEL])
        logger.error("\n".join(lines))
        return True
    return False


def get_skipped_files() -> list[str]:
    """Get the list of skipped files."""
    return files_skipped
