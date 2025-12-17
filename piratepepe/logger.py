"""Logging configuration for archivepodcast."""

import logging
from logging import StreamHandler
from typing import Any, cast

from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
from rich.theme import Theme

DESIRED_LEVEL_NAME_LEN = 5
DESIRED_NAME_LEN = 16
DESIRED_THREAD_NAME_LEN = 13


LOG_LEVELS = [
    "TRACE",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]  # Valid str logging levels.


MIN_LOG_LEVEL_INT = 0
MAX_LOG_LEVEL_INT = 50


TRACE_LEVEL_NUM = 5


class CustomLogger(logging.Logger):
    """Custom logger to appease mypy."""

    def trace(self, message: object, *args: Any, **kws: Any) -> None:  # noqa: ANN401
        """Create logger level for trace."""
        if self.isEnabledFor(TRACE_LEVEL_NUM):
            # Yes, logger takes its '*args' as 'args'.
            self._log(TRACE_LEVEL_NUM, message, args, **kws)


logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
logging.setLoggerClass(CustomLogger)

# This is where we log to in this module, following the standard of every module.
# I don't use the function so we can have this at the top
logger = cast("CustomLogger", logging.getLogger(__name__))


# Pass in the whole app object to make it obvious we are configuring the logger object within the app object.
def setup_logger(
    verbosity: int = 0,
    in_logger: logging.Logger | None = None,
) -> None:
    """Configure logging for the application."""
    level = get_verbosity_cli(verbosity)

    if not in_logger:  # in_logger should only exist when testing with PyTest.
        in_logger = logging.getLogger()  # Get the root logger

    # If the logger doesn't have a console handler (root logger doesn't by default)
    if not _has_console_handler(in_logger):
        _add_console_handler(in_logger)

    _set_log_level(in_logger, level)

    # Configure modules that are external and have their own loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # Bit noisy when set to info, used by requests module.

    logger.debug("Logger configuration set!")


def get_logger(name: str) -> CustomLogger:
    """Get a logger with the name provided."""
    return cast("CustomLogger", logging.getLogger(name))


def _has_console_handler(in_logger: logging.Logger) -> bool:
    """Check if logger has a console handler."""
    return any(isinstance(handler, (RichHandler, StreamHandler)) for handler in in_logger.handlers)


def _add_console_handler(
    in_logger: logging.Logger,
) -> None:
    """Add a console handler to the logger."""
    console = Console(theme=Theme({"logging.level.trace": "dim"}))
    rich_handler = RichHandler(
        console=console,
        show_time=False,
        rich_tracebacks=True,
        highlighter=NullHighlighter(),
    )
    in_logger.addHandler(rich_handler)


def _set_log_level(in_logger: logging.Logger, log_level: int | str) -> None:
    """Set the log level of the logger."""
    if isinstance(log_level, str):
        log_level = log_level.upper()
        if log_level not in LOG_LEVELS:
            in_logger.setLevel("INFO")
            logger.warning(
                "❗ Invalid logging level: %s, defaulting to INFO",
                log_level,
            )
        else:
            in_logger.setLevel(log_level)
            logger.debug("Showing log level: DEBUG")
            logger.trace("Showing log level: TRACE")
    else:
        in_logger.setLevel(log_level)


def get_verbosity_cli(verbosity: int) -> None:
    """Get verbosity level from CLI argument."""
    if verbosity >= 2:  # noqa: PLR2004 Magic number makes sense
        return TRACE_LEVEL_NUM
    if verbosity == 1:
        return logging.DEBUG

    return logging.INFO
