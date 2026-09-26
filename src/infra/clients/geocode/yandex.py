import logging

import httpx
from core.clients.geocode.base_client import BaseGeoCodeClient
from core.clients.geocode.exceptions import GeocodeNotFound

logger = logging.getLogger(__name__)


class YandexGeoCodeClient(BaseGeoCodeClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://geocode-maps.yandex.ru/v1/"

    # TODO(sxtxri): модель респонса на сервисе должна обрабатываться
    async def geocode(self, address: str) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.url,
                    params={"apikey": self.api_key, "geocode": address,
                            "format": "json", "results": 1},
                    timeout=5.0,
                )
                response.raise_for_status()

                members = response.json()["response"]["GeoObjectCollection"]["featureMember"]
                pos = members[0]["GeoObject"]["Point"]["pos"]
                lon, lat = map(float, pos.split())
                return {"lat": lat, "lon": lon}

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Yandex geocoder HTTP %s for address %r: %s",
                    e.response.status_code, address, e.response.text[:500],
                )
                raise GeocoderFailure(
                    f"Yandex API failure: HTTP {e.response.status_code}"
                ) from e
            except (httpx.HTTPError, KeyError, IndexError, ValueError) as e:
                logger.error("Yandex geocoder %s for address %r: %s",
                             type(e).__name__, address, type(e).__name__)
                raise GeocoderFailure(f"Yandex API failure: {type(e).__name__}") from e