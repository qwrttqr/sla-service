import logging

import httpx

from common.types import GeoPoint
from core.clients.geocode.base_client import BaseGeoCodeClient
from core.clients.geocode.exceptions import GeocodeNotFound
from core.clients.geocode.schemas import GeocoderRequest, GeocoderResponse

logger = logging.getLogger(__name__)


class YandexGeoCodeClient(BaseGeoCodeClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://geocode-maps.yandex.ru/v1/"

    async def geocode(self, req: GeocoderRequest) -> GeocoderResponse | GeocodeNotFound:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.url,
                    params={
                        "apikey": self.api_key,
                        "geocode": req.address,
                        "format": "json",
                        "results": 1,
                    },
                    timeout=5.0,
                )
                response.raise_for_status()

                members = response.json()["response"]["GeoObjectCollection"][
                    "featureMember"
                ]
                pos = members[0]["GeoObject"]["Point"]["pos"]
                lon, lat = map(float, pos.split())
                return GeocoderResponse(point=GeoPoint(lon=lon, lat=lat))

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Yandex geocoder HTTP %s for address %r: %s",
                    e.response.status_code,
                    req.address,
                    e.response.text[:500],
                )
                return GeocodeNotFound()
