import asyncio
from argparse import ArgumentError
from typing import Tuple

from core.clients.geocode.base_client import BaseGeoCodeClient


class GeocoderService:
    def __init__(self, client: BaseGeoCodeClient, rate_limit_delay: float = 0.5):
        self.client = client
        self._semaphore = asyncio.Semaphore(1)
        self._rate_limit_delay = rate_limit_delay

    async def get_coordinates(self, address: str) -> Tuple[float, float]:
        """
        Converts a string address into a coordinate tuple (lat, lon)
        """
        # TODO(sxtxri): чет с этим сделать надо
        # TODO(sxtxri): сервис плюс с кэшом должен работать
        if not address or not isinstance(address, str):
            raise ArgumentError("address should be str and not None")

        async with self._semaphore:
            coords = await self.client.geocode(address.strip())
            await asyncio.sleep(self._rate_limit_delay)
        # TODO(sxtxri): коорды вынести моделькой в базовые типы
        return float(coords["lat"]), float(coords["lon"])