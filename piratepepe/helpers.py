"""Helper functions for PiratePepe."""

from pydantic import ValidationError

from .constants import PEPES_TXT
from .logger import get_logger

logger = get_logger(__name__)


def scan_pepe_file() -> list[str]:
    """Scan pepe_txt var for ipfs links."""
    pepe_list_str = PEPES_TXT

    listfresh: list[str] = []
    for element in pepe_list_str.split():
        # Ignore everything that doesn't start with a Q since that's what all them things seem to start with
        if element[0] == "Q":
            listfresh.append(element.strip())
        else:
            logger.debug("Not a pepe: %s", element.strip())
    pepe_list = listfresh
    logger.debug("Pepe list: [%s", pepe_list)

    logger.info("Found %d tokenURIs to look for Pepe", len(pepe_list))

    return pepe_list


def summarize_validation_error(context: str, e: ValidationError) -> None:
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

    # Build single message and log once
    lines = ["Validation error:", f" {context}"]
    if missing:
        lines.append("  Missing fields: " + ", ".join(missing))
    if extra:
        lines.append("  Extra fields: " + ", ".join(extra))
    if invalid:
        lines.extend([f"  Invalid field: {inv['field']} - Reason: {inv['reason']}" for inv in invalid])

    logger.error("\n".join(lines))
