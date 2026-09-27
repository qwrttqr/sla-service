from abc import ABC, abstractmethod
from core.clients.geocode.exceptions import GeocodeNotFound
from core.clients.geocode.schemas import GeocoderRequest, GeocoderResponse


class BaseGeoCodeClient(ABC):
    """
    Базовый класс для поиска адресов и геокодировки.
    """

    @abstractmethod
    async def geocode(self, req: GeocoderRequest) -> GeocoderResponse| GeocodeNotFound:
        raise NotImplementedError
