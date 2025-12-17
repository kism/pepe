"""Configuration and shared state for piratepepe."""


class AppConfig:
    """Application configuration and shared state."""

    def __init__(
        self,
        output_folder: str = "output",
        start_point: int = 0,
        http_timeout: int = 5,
        *,
        debug: bool = False,
        slow_mode: bool = False,
    ) -> None:
        """Initialize configuration."""
        self.debug = debug
        self.output_folder = output_folder
        self.start_point = start_point
        self.slow_mode = slow_mode
        self.http_timeout = http_timeout
        self.headers = {"User-Agent": "Safari/537.3"}

config = AppConfig()
