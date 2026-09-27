from common.types import GeoPoint, VehicleType
from core.clients.travel_time.base_client import BaseTravelTimeClient
from core.clients.travel_time.exceptions import TravelTimeUnavailable
from core.clients.travel_time.schemas import TravelTimeRequest


class TravelTimeService:
    def __init__(
        self,
        osrm_car_client: BaseTravelTimeClient,
        osrm_bicycle_client: BaseTravelTimeClient,
        osrm_foot_client: BaseTravelTimeClient,
    ):
        self._osrm_car_client = osrm_car_client
        self._osrm_bicycle_client = osrm_bicycle_client
        self._osrm_foot_client = osrm_foot_client

    async def get_matrix(
        self,
        origins: list[GeoPoint],
        destinations: list[GeoPoint],
        vehicle_type: VehicleType,
    ) -> list[list[float | None]]:
        """
        Returns matrix of travel time as cartesian prodict of origins to destinations
        Raises:
            TravelTimeUnavailable - when client cannot satisfy request
        """
        vehicle_profile = vehicle_type.vehicle_profile()

        req = TravelTimeRequest(
            origins=origins, destinations=destinations, profile=vehicle_profile
        )
        # TODO(sxtxri): мб в отдельный внутренний метод вынести?)
        if vehicle_type == VehicleType.CAR:
            result = await self._osrm_car_client.matrix_minutes(req)
        elif vehicle_type == VehicleType.BICYCLE:
            result = await self._osrm_car_client.matrix_minutes(req)
        elif vehicle_type == VehicleType.BICYCLE:
            result = await self._osrm_car_client.matrix_minutes(req)
        else:
            # TODO(sxtxri): нужна отдельная ошибка что этот вид тс не поддерживаем
            raise TravelTimeUnavailable()

        if isinstance(result, TravelTimeUnavailable):
            raise result

        return result.durations_minutes
