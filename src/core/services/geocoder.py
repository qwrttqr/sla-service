import asyncio

from common.types import GeoPoint
from core.clients.geocode.base_client import BaseGeoCodeClient
from core.clients.geocode.exceptions import GeocodeNotFound
from core.clients.geocode.schemas import GeocoderRequest
from common.types import GeoPoint


class GeocoderService:
    def __init__(self, client: BaseGeoCodeClient, rate_limit_delay: float = 0.3):
        self.client = client
        self._semaphore = asyncio.Semaphore(1)
        self._rate_limit_delay = rate_limit_delay

    async def get_coordinates(self, address: str) -> GeoPoint:
        """
        Converts a string address into a coordinate.
        Raises:
            GeocodeNotFound
        """
        # TODO(sxtxri): чет с этим сделать надо
        if not address or not isinstance(address, str):
            raise ValueError("address should be a non-empty str")

        async with self._semaphore:
            response = await self.client.geocode(GeocoderRequest(address=address))
            await asyncio.sleep(self._rate_limit_delay)

        if isinstance(response, GeocodeNotFound):
            raise response

        return GeoPoint(response.latitude, response.longitude)