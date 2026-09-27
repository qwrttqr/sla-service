from common.types import GeoPoint
from core.clients.travel_time.base_client import BaseTravelTimeClient
from core.clients.travel_time.exceptions import TravelTimeUnavailable
from core.clients.travel_time.schemas import TravelTimeRequest


class TravelTimeService:
    def __init__(self, client: BaseTravelTimeClient):
        self.client = client

    async def get_matrix(
        self, origins: list[GeoPoint], destinations: list[GeoPoint], profile: str
    ) -> list[list[float | None]]:
        """
        Returns matrix of travel time as cartesian prodict of origins to destinations
        Raises:
            TravelTimeUnavailable - when client cannot satisfy request
        """
        req = TravelTimeRequest(origins=origins, destinations=destinations, profile=profile)
        result = await self.client.matrix_minutes(req)

        if isinstance(result, TravelTimeUnavailable):
            raise result

        return result.durations_minutes