"""Track files that failed to download."""

files_skipped: list[str] = []


def add_skipped_file(filename: str) -> None:
    """Add a file to the skipped files list."""
    files_skipped.append(filename)


def has_skipped_files() -> bool:
    """Check if any files were skipped."""
    return len(files_skipped) > 0


def get_skipped_files() -> list[str]:
    """Get the list of skipped files."""
    return files_skipped
