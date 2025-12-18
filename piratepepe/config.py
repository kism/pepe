"""Configuration and shared state for piratepepe."""

from dataclasses import dataclass, field
from pathlib import Path

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class AppConfig:
    """Application configuration and shared state."""

    output_folder: Path = Path("output")
    http_timeout: int = 5
    slow_mode: bool = False
    headers: dict[str, str] = field(default_factory=lambda: {"User-Agent": "Safari/537.3"})

    def validate(self) -> None:
        """Validate configuration."""
        if not self.output_folder.exists():
            logger.info("Creating output folder at %s", self.output_folder)
            self.output_folder.mkdir(parents=True, exist_ok=True)
        elif not self.output_folder.is_dir():
            msg = f"Output folder path {self.output_folder} exists and is not a directory."
            raise ValueError(msg)


config = AppConfig()
