from argparse import ArgumentError
from typing import Tuple

from src.core.domain.geocoder_interface import GeocoderInterface


class GeocoderService:
    def __init__(self, provider: GeocoderInterface):
        self.provider = provider

    async def get_coordinates(self, address: str) -> Tuple[float, float]:
        """
        Converts a string address into a coordinate tuple (lat, lon)
        """
        if not address or not isinstance(address, str):
            raise ArgumentError("address should be str and not None")

        coords = await self.provider.geocode(address.strip())
        return float(coords["lat"]), float(coords["lon"])
