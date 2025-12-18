"""IPFS Gateway handler with weighted selection based on failure tracking."""

import random
from collections import Counter
from collections.abc import Callable, Generator

from .constants import IPFS_GATEWAY_LIST
from .logger import get_logger

logger = get_logger(__name__)
_MAX_WEIGHT = 10.0
_INITIAL_WEIGHT = 1.0


class IPFSGateway:
    """Represents an IPFS gateway with its weight, failure count, and failure reasons."""

    def __init__(self, url: str, weight: float = _INITIAL_WEIGHT) -> None:
        """Initialize gateway with URL and optional weight."""
        self.url = url
        self.weight = weight
        self.failures = 0
        self.successes = 0
        self.failure_reasons: list[str] = []

    def reduce_weight(self, reason: str) -> None:
        """Reduce weight due to failure."""
        self.weight *= 0.5
        self.failures += 1
        self.failure_reasons.append(reason)

    def increase_weight(self) -> None:
        """Increase weight due to success."""
        self.weight = min(self.weight * 1.5, _MAX_WEIGHT)
        self.successes += 1

    def __repr__(self) -> str:
        """String representation of the gateway."""
        return f"IPFSGateway(url={self.url}, weight={self.weight:.3f}, failures={self.failures})"


class GatewayAttempt:
    """Represents a single attempt to use a gateway with tracking methods."""

    def __init__(self, handler: "IPFSGatewayHandler", url: str) -> None:
        """Initialize with handler reference and gateway URL."""
        self.handler = handler
        self.url = url

    def report_success(self) -> None:
        """Report that this gateway succeeded."""
        self.handler.increase_weight(self.url)

    def report_failure(self, reason: str) -> None:
        """Report that this gateway failed with a reason."""
        self.handler.reduce_weight(self.url, reason)


class IPFSGatewayHandler:
    """Manages IPFS gateways with weighted random selection based on failure rates."""

    def __init__(self, gateways: list[str]) -> None:
        """Initialize with a list of gateways."""
        gateway_urls = self._deduplicate_gateways(gateways)
        self.gateways: dict[str, IPFSGateway] = {url: IPFSGateway(url) for url in gateway_urls}

    def _deduplicate_gateways(self, gateways: list[str]) -> list[str]:
        """Remove duplicate gateways and warn about them."""
        for item, count in Counter(gateways).items():
            if count > 1:
                logger.info("Duplicate gateway: %s", item)
        return list(dict.fromkeys(gateways))

    def get_gateway(self, gateway_url: str) -> IPFSGateway:
        """Add a new gateway if it doesn't exist."""
        if gateway_url not in self.gateways:
            self.gateways[gateway_url] = IPFSGateway(gateway_url)

        return self.gateways[gateway_url]

    def reduce_weight(self, gateway_url: str, reason: str) -> None:
        """Reduce the weight of a gateway due to failure."""
        gw = self.get_gateway(gateway_url)
        gw.reduce_weight(reason)

        logger.debug(
            "Gateway: %s failed (%s), new weight: %.3f %s/%s",
            gateway_url,
            reason,
            gw.weight,
            gw.successes,
            (gw.successes + gw.failures),
        )

    def increase_weight(self, gateway_url: str) -> None:
        """Increase the weight of a gateway due to success."""
        gw = self.get_gateway(gateway_url)
        gw.increase_weight()

        logger.debug(
            "Gateway: %s succeeded, new weight: %.3f %s/%s",
            gateway_url,
            gw.weight,
            gw.successes,
            (gw.successes + gw.failures),
        )

    def get_weighted_gateways(self) -> list[str]:
        """Get gateways sorted by weighted random selection."""
        items = list(self.gateways.items())

        # Sort by weighted random key
        return [url for url, _ in sorted(items, key=lambda x: random.random() ** (1 / x[1].weight))]

    def iterate_gateways(self) -> "Generator[GatewayAttempt, None, None]":
        """Iterate through gateways in weighted order with success/failure tracking.

        Yields gateway URLs one at a time. Use report_success() or report_failure()
        to update gateway weights.

        Example:
            for gateway in handler.iterate_gateways():
                try:
                    result = fetch_from_gateway(gateway.url)
                    gateway.report_success()
                    return result
                except Exception as e:
                    gateway.report_failure(str(e))
        """
        for gateway_url in self.get_weighted_gateways():
            yield GatewayAttempt(self, gateway_url)

    def try_gateways(self, callback: Callable[[str], tuple[bool, str | None]]) -> bool:
        """Try gateways in weighted order using the provided callback.

        Deprecated: Use iterate_gateways() for more flexibility.
        """
        for gateway_url in self.get_weighted_gateways():
            success, failure_reason = callback(gateway_url)

            if success:
                self.increase_weight(gateway_url)
                return True
            if failure_reason:
                self.reduce_weight(gateway_url, failure_reason)

        return False

    def print_statistics(self) -> None:
        """Print gateway statistics."""
        lines = ["Gateway Statistics:"]
        sorted_gateways = sorted(self.gateways.items(), key=lambda x: (x[1].successes, -x[1].failures), reverse=True)
        for gw_url, gw in sorted_gateways:
            total = gw.successes + gw.failures
            ratio = f"{gw.successes}/{total}"
            lines.append(f"{ratio:>6} | {gw_url}")

        msg = "\n".join(lines)
        logger.info(msg)


gateway_handler = IPFSGatewayHandler(IPFS_GATEWAY_LIST)
