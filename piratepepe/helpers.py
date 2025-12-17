"""Helper functions for PiratePepe."""

from pathlib import Path

import magic
from colorama import Fore, Style
from pydantic import ValidationError

from .config import config
from .constants import PEPES_TXT


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


def check_file(file_path: Path) -> bool:
    """Check if a file is heck."""
    mime = magic.Magic(mime=True, uncompress=True)

    try:
        file_type = mime.from_file(str(file_path))
        print(f"Found file type: {file_type}")
        return file_type.startswith("text")
    except FileNotFoundError:
        return False


def summarize_validation_error(e: ValidationError) -> None:
    """Summarize Pydantic validation errors for debugging."""
    missing = []
    extra = []
    invalid = []

    for err in e.errors():
        field = ".".join(str(x) for x in err["loc"])
        err_type = err["type"]

        if err_type == "missing":
            missing.append(field)
        elif err_type == "extra_forbidden":
            extra.append(field)
        else:
            invalid.append(
                {
                    "field": field,
                    "reason": err["msg"],
                }
            )

    print_debug("Validation Error Summary:")
    if missing:
        print_debug(f"  Missing fields: {', '.join(missing)}")
    if extra:
        print_debug(f"  Extra fields: {', '.join(extra)}")
    if invalid:
        for inv in invalid:
            print_debug(f"  Invalid field: {inv['field']} - Reason: {inv['reason']}")
