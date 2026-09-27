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
        self._clients: dict[VehicleType, BaseTravelTimeClient] = {
            VehicleType.CAR: osrm_car_client,
            VehicleType.BICYCLE: osrm_bicycle_client,
            VehicleType.WALK: osrm_foot_client,
        }

    async def get_matrix(
        self,
        origins: list[GeoPoint],
        destinations: list[GeoPoint],
        vehicle_type: VehicleType,
    ) -> list[list[float | None]]:
        client = self._clients.get(vehicle_type)
        if client is None:
            # TODO(sxtxri): нужна отдельная ошибка что этот вид тс не поддерживаем
            raise TravelTimeUnavailable()

        req = TravelTimeRequest(
            origins=origins,
            destinations=destinations,
            profile=vehicle_type.vehicle_profile(),
        )
        result = await client.matrix_minutes(req)

        if isinstance(result, TravelTimeUnavailable):
            raise result

        return result.durations_minutes
