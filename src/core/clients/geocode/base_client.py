from abc import ABC, abstractmethod
from core.clients.geocode.exceptions import GeocodeNotFound


class BaseGeoCodeClient(ABC):
    """
    Базовый класс для поиска адресов и геокодировки.
    """

    # TODO(sxtxri): сюда по хорошему модель реквеста передать (клиент как никак...)
    # TODO(sxtxri): сделать модельку под респонс
    @abstractmethod
    async def geocode(self, address: str) -> dict[str, float] | GeocodeNotFound:
        raise NotImplementedError
