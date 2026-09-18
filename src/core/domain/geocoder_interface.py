from abc import ABC, abstractmethod
from typing import Dict, Any


class GeocoderInterface(ABC):
    """
    Abstract interface for all Geocoding services.
    """

    @abstractmethod
    async def geocode(self, address: str) -> Dict[str, Any]:
        """
        Convert a text address into geographic coordinates.
        Should return a standardized dictionary, e.g., {'lat': float, 'lon': float}
        """
        pass
