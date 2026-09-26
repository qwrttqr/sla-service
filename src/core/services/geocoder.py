import asyncio
from argparse import ArgumentError
from typing import Tuple

from core.services.geocoder_interface import GeocoderInterface


class GeocoderService:
    def __init__(self, provider: GeocoderInterface, rate_limit_delay: float = 0.5):
        self.provider = provider
        self._semaphore = asyncio.Semaphore(1)
        self._rate_limit_delay = rate_limit_delay

    async def get_coordinates(self, address: str) -> Tuple[float, float]:
        """
        Converts a string address into a coordinate tuple (lat, lon)
        """
        if not address or not isinstance(address, str):
            raise ArgumentError("address should be str and not None")

        async with self._semaphore:
            coords = await self.provider.geocode(address.strip())
            await asyncio.sleep(self._rate_limit_delay)
        return float(coords["lat"]), float(coords["lon"])