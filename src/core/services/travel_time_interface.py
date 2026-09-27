from abc import ABC, abstractmethod
from datetime import datetime

from common.types import VehicleType, GeoPoint


class TravelTimeInterface(ABC):
    """Abstract interface for all travel time services."""

    @abstractmethod
    async def matrix_minutes(
        self,
        origins: list[GeoPoint],
        destinations: list[GeoPoint],
        vehicle: VehicleType,
        departure: datetime,
    ) -> list[list[float | None]]:
        """
        Travel minutes for every origin -> destination pair, traffic included.
        None means the pair is unroutable.
        """