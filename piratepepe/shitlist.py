"""Track gateway failures for Pirate Pepe NFT fetching."""

from pydantic import BaseModel

from .logger import get_logger

logger = get_logger(__name__)


class GatewayFailures(BaseModel):
    """Type definition for gateway failure tracking."""

    nfails: int
    fails: dict[str, int]


class Shitlist(dict[str, GatewayFailures]):
    """Track gateway failures with automatic tallying."""

    def add_failure(self, gateway: str, error: str) -> None:
        """Keep a tally of gateway failures."""
        logger.error("Gateway failure: %s", error)

        if gateway not in self:
            self[gateway] = GatewayFailures(nfails=0, fails={})

        self[gateway].nfails += 1

        if error not in self[gateway].fails:
            self[gateway].fails[error] = 0
        self[gateway].fails[error] += 1

    def print_scoreboard(self) -> None:
        """Print the IPFS gateway failure scoreboard."""
        if not self:
            return

        spacing = " " * 4

        lines: list[str] = ["ipfs gateway scoreboard:"]
        sorted_shitlist = dict(sorted(self.items(), key=lambda item: item[1].nfails, reverse=True))
        for gateway, failures in sorted_shitlist.items():
            lines.append("")
            lines.append(f"{spacing}Gateway: {gateway}")
            lines.append(f"{spacing}Total Fails: {failures.nfails}")
            sorted_fails = dict(sorted(failures.fails.items(), key=lambda item: item[1], reverse=True))
            for error, count in sorted_fails.items():
                lines.append(f"{spacing * 3}{count} {error}")
        logger.info("\n".join(lines))
