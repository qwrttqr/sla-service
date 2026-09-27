from common.types import GeoPoint, VehicleType
from core.clients.travel_time.base_client import BaseTravelTimeClient
from core.clients.travel_time.exceptions import TravelTimeUnavailable, TravelTimeUnsupportedTransportType
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
        profile = vehicle_type.vehicle_profile()

        if client is None or profile is None:
            # нет OSRM-профиля для этого типа транспорта (например, public_transport)
            raise TravelTimeUnsupportedTransportType(f"Данный тип транспорта в данный момент не поддерживается {vehicle_type}")

        req = TravelTimeRequest(
            origins=origins,
            destinations=destinations,
            profile=profile,
        )
        result = await client.matrix_minutes(req)

        if isinstance(result, TravelTimeUnavailable):
            raise result

        return result.durations_minutes

    def assert_transport_type_supported(self, transport_type: str):
        if not transport_type in self._clients.keys():
            raise TravelTimeUnsupportedTransportType(f"Данный тип транспорта в данный момент не поддерживается {transport_type}")