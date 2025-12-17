"""Data models for Pirate Pepe NFTs."""

from pydantic import BaseModel, ConfigDict


class Attribute(BaseModel):
    """An attribute of the NFT."""

    model_config = ConfigDict(extra="forbid")

    trait_type: str
    value: str | int | float
    display_type: str | None = None


class HifiMedia(BaseModel):
    """High fidelity media URLs for the NFT."""

    model_config = ConfigDict(extra="forbid")

    video: str
    card_front: str | None = None
    card_back: str | None = None


class PepeNFT(BaseModel):
    """Pepe NFT metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    tokenId: int  # noqa: N815
    external_url: str
    image: str
    animation_url: str
    hifi_media: HifiMedia
    attributes: list[Attribute]
