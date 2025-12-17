"""IPFS Gateway handler with weighted selection based on failure tracking."""

import random
from collections import Counter
from collections.abc import Callable

from .config import config


class IPFSGatewayHandler:
    """Manages IPFS gateways with weighted random selection based on failure rates."""

    def __init__(self, gateways: list[str]) -> None:
        """Initialize with a list of gateways."""
        self.gateways = self._deduplicate_gateways(gateways)
        self.weights = dict.fromkeys(self.gateways, 1.0)
        self.failures: dict[str, int] = {}
        self.failure_reasons: dict[str, list[str]] = {}

    def _deduplicate_gateways(self, gateways: list[str]) -> list[str]:
        """Remove duplicate gateways and warn about them."""
        for item, count in Counter(gateways).items():
            if count > 1:
                print(f"Duplicate gateway: {item}")
        return list(dict.fromkeys(gateways))

    def add_gateway(self, gateway: str) -> None:
        """Add a new gateway if it doesn't exist."""
        if gateway not in self.weights:
            self.gateways.append(gateway)
            self.weights[gateway] = 1.0

    def reduce_weight(self, gateway: str, reason: str) -> None:
        """Reduce the weight of a gateway due to failure."""
        if gateway in self.weights:
            self.weights[gateway] *= 0.5
            self.failures[gateway] = self.failures.get(gateway, 0) + 1

            if gateway not in self.failure_reasons:
                self.failure_reasons[gateway] = []
            self.failure_reasons[gateway].append(reason)

            if config.debug:
                print(f"Gateway {gateway} failed ({reason}), new weight: {self.weights[gateway]:.3f}")

    def increase_weight(self, gateway: str) -> None:
        """Increase the weight of a gateway due to success."""
        if gateway in self.weights:
            self.weights[gateway] = min(self.weights[gateway] * 1.5, 10.0)

            if config.debug:
                print(f"Gateway {gateway} succeeded, new weight: {self.weights[gateway]:.3f}")

    def get_weighted_gateways(self) -> list[str]:
        """Get gateways sorted by weighted random selection."""
        gateways = list(self.weights.keys())
        weights = [self.weights[g] for g in gateways]

        # Return all gateways but sorted by weighted random
        # Sample without replacement to get all gateways in weighted order
        result = []
        remaining_gateways = gateways[:]
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
        for gateway in self.get_weighted_gateways():
            success, failure_reason = callback(gateway)

            if success:
                self.increase_weight(gateway)
                return True
            if failure_reason:
                self.reduce_weight(gateway, failure_reason)
                print("trying next gateway...")

        return False

    def print_statistics(self) -> None:
        """Print gateway failure statistics."""
        if not self.failures:
            return

        print("\nGateway Statistics:")
        sorted_gateways = sorted(self.failures.items(), key=lambda x: x[1], reverse=True)
        for gateway, failure_count in sorted_gateways:
            weight = self.weights.get(gateway, 0)
            print(f"  {gateway}: {failure_count} failures (weight: {weight:.3f})")
