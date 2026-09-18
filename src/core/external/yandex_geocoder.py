import httpx
from src.core.domain.geocoder_interface import GeocoderInterface
from core.exceptions.geocoder_failure import GeocoderFailure


class YandexGeocoder(GeocoderInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://yandex.ru"

    async def geocode(self, address: str) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.url,
                    params={"apikey": self.api_key, "geocode": address, "format": "json"},
                    timeout=5.0
                )
                response.raise_for_status()

                data = response.json()
                pos = data['response']['GeoObjectCollection']['featureMember']['GeoObject']['Point']['pos']
                lon, lat = map(float, pos.split())

                return {"lat": lat, "lon": lon}

            except (httpx.HTTPError, KeyError, IndexError, ValueError) as origin_error:
                raise GeocoderFailure(f"Yandex API failure: {origin_error}") from origin_error
