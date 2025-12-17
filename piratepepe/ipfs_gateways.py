"""IPFS Gateway handler with weighted selection based on failure tracking."""

import random
from collections import Counter
from collections.abc import Callable

from .config import config
from .constants import IPFS_GATEWAY_LIST

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
                print(f"Duplicate gateway: {item}")
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

        if config.debug:
            print(f"Gateway {gateway_url} failed ({reason}), new weight: {gw.weight:.3f}")

    def increase_weight(self, gateway_url: str) -> None:
        """Increase the weight of a gateway due to success."""
        gw = self.get_gateway(gateway_url)
        gw.increase_weight()

        if config.debug:
            print(f"Gateway {gateway_url} succeeded, new weight: {gw.weight:.3f}")

    def get_weighted_gateways(self) -> list[str]:
        """Get gateways sorted by weighted random selection."""
        gateway_urls = list(self.gateways.keys())
        weights = [self.gateways[url].weight for url in gateway_urls]

        # Return all gateways but sorted by weighted random
        # Sample without replacement to get all gateways in weighted order
        result = []
        remaining_gateways = gateway_urls[:]
        remaining_weights = weights[:]

        while remaining_gateways:
            selected = random.choices(remaining_gateways, weights=remaining_weights, k=1)[0]
            result.append(selected)
            idx = remaining_gateways.index(selected)
            remaining_gateways.pop(idx)
            remaining_weights.pop(idx)

        return result

    def try_gateways(self, callback: Callable[[str], tuple[bool, str | None]]) -> bool:
        """Try gateways in weighted order using the provided callback."""
        for gateway_url in self.get_weighted_gateways():
            success, failure_reason = callback(gateway_url)

            if success:
                self.increase_weight(gateway_url)
                return True
            if failure_reason:
                self.reduce_weight(gateway_url, failure_reason)
                print("trying next gateway...")

        return False

    def print_statistics(self) -> None:
        """Print gateway failure statistics."""
        gateways_with_failures = {url: gw for url, gw in self.gateways.items() if gw.failures > 0}
        if not gateways_with_failures:
            return

        print("\nGateway Statistics:")
        sorted_gateways = sorted(gateways_with_failures.items(), key=lambda x: x[1].failures, reverse=True)
        for gateway_url, gateway in sorted_gateways:
            print(f"  {gateway_url}: {gateway.failures} failures, {gateway.successes} successes")


gateway_handler = IPFSGatewayHandler(IPFS_GATEWAY_LIST)
