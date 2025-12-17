"""Track files that failed to download."""

from colorama import Fore, Style

files_skipped: list[str] = []


def add_skipped_file(filename: str) -> None:
    """Add a file to the skipped files list."""
    files_skipped.append(filename)


def has_skipped_files() -> bool:
    """Check if any files were skipped."""
    if len(files_skipped) > 0:
        print("Some Downloads failed")
        print()
        print(f"{Fore.RED}Missing Pepe Assets{Style.RESET_ALL}:")
        for file in get_skipped_files():
            print(f" {file}")
        print()
        print("Run the script again to try again.")
        print(
            "You might want to find some new ipfs gateways and add them to the script, "
            "or get a new IP address since some ipfs gateways will rate-limit or block you for downloading too much.",
        )
        return True
    return False


def get_skipped_files() -> list[str]:
    """Get the list of skipped files."""
    return files_skipped
