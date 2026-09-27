from abc import ABC, abstractmethod
from datetime import datetime

from core.entities import VehicleType

Coords = tuple[float, float]  # (lat, lon)


class TravelTimeInterface(ABC):
    """Abstract interface for all travel time services."""

    @abstractmethod
    async def matrix_minutes(
        self,
        origins: list[Coords],
        destinations: list[Coords],
        vehicle: VehicleType,
        departure: datetime,
    ) -> list[list[float | None]]:
        """
        Travel minutes for every origin -> destination pair, traffic included.
        None means the pair is unroutable.
        """