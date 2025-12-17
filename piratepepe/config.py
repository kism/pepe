"""Configuration and shared state for piratepepe."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    """Application configuration and shared state."""

    output_folder: Path = Path("output")
    start_point: int = 0
    http_timeout: int = 5
    debug: bool = False
    slow_mode: bool = False
    headers: dict[str, str] = field(default_factory=lambda: {"User-Agent": "Safari/537.3"})

    def validate(self) -> None:
        """Validate configuration."""
        if self.start_point < 0:
            print("Start point cannot be negative. Setting to 0.")
            self.start_point = 0

        if not self.output_folder.exists():
            print(f"Creating output folder at {self.output_folder}")
            self.output_folder.mkdir(parents=True, exist_ok=True)
        elif not self.output_folder.is_dir():
            msg = f"Output folder path {self.output_folder} exists and is not a directory."
            raise ValueError(msg)


config = AppConfig()
