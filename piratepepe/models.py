"""Data models for Pirate Pepe NFTs."""

from dataclasses import dataclass


@dataclass
class HifiMedia:
    """High fidelity media URLs for the NFT."""

    video: str
    card_front: str | None = None
    card_back: str | None = None


@dataclass
class PepeNFT:
    """Pepe NFT metadata."""

    name: str
    image: str
    animation_url: str
    hifi_media: HifiMedia
