from abc import ABC, abstractmethod

from core.clients.travel_time.exceptions import TravelTimeUnavailable
from core.clients.travel_time.schemas import (TravelTimeRequest,
                                              TravelTimeResponse)


class BaseTravelTimeClient(ABC):
    @abstractmethod
    async def matrix_minutes(
        self, req: TravelTimeRequest
    ) -> TravelTimeResponse | TravelTimeUnavailable:
        raise NotImplementedError
    def is_transport_type_supported(self, transport_type: str) -> bool:
        raise NotImplementedError
    async def aclose(self) -> None:
        """Optional resource cleanup; override if the client owns a connection."""
