"""Track gateway failures for Pirate Pepe NFT fetching."""

from typing import TypedDict

from colorama import Fore, Style


class GatewayFailures(TypedDict):
    """Type definition for gateway failure tracking."""

    nfails: int
    fails: dict[str, int]


class Shitlist(dict[str, GatewayFailures]):
    """Track gateway failures with automatic tallying."""

    def add_failure(self, gateway: str, error: str) -> None:
        """Keep a tally of gateway failures."""
        print(f"{Fore.RED}Gateway failure{Style.RESET_ALL}: {error}")

        if gateway not in self:
            self[gateway] = {"nfails": 0, "fails": {}}

        self[gateway]["nfails"] += 1

        if error not in self[gateway]["fails"]:
            self[gateway]["fails"][error] = 0
        self[gateway]["fails"][error] += 1

    def print_scoreboard(self) -> None:
        """Print the IPFS gateway failure scoreboard."""
        if len(self.items()) > 0:
            print("ipfs gateway scoreboard:")
            sorted_shitlist = dict(sorted(self.items(), key=lambda item: item[1]["nfails"], reverse=True))
            for gateway, failures in sorted_shitlist.items():
                print()
                print(f"    Gateway: {gateway}")
                print(f"Total Fails: {failures['nfails']}")
                sorted_fails = dict(sorted(failures["fails"].items(), key=lambda item: item[1], reverse=True))
                for error, count in sorted_fails.items():
                    print(f"               {count} {error}")
