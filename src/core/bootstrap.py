import functools

from config import settings
from core.clients.geocode.base_client import BaseGeoCodeClient
from core.clients.travel_time.base_client import BaseTravelTimeClient
from core.services.data_processing.engineers import EngineerBuilder
from core.services.data_processing.requests import RequestBuilder
from core.services.geocoder import GeocoderService
from core.services.planner import PlannerService
from core.services.travel_time import TravelTimeService
from infra.clients.geocode.yandex import YandexGeoCodeClient
from infra.clients.travel_time.osrm import OsrmTravelTimeClient


@functools.cache
def get_yandex_geocode_client() -> BaseGeoCodeClient:
    return YandexGeoCodeClient(settings.yandex_geocoder_api_key.get_secret_value())


@functools.cache
def get_geocoder_service() -> GeocoderService:
    return GeocoderService(get_yandex_geocode_client())


@functools.cache
def get_engineer_builder() -> EngineerBuilder:
    return EngineerBuilder(get_geocoder_service())


@functools.cache
def get_request_builder() -> RequestBuilder:
    return RequestBuilder(get_geocoder_service())


@functools.cache
def get_osrm_car_client() -> BaseTravelTimeClient:
    return OsrmTravelTimeClient(settings.osrm_car_url)


@functools.cache
def get_osrm_bicycle_client() -> BaseTravelTimeClient:
    return OsrmTravelTimeClient(settings.osrm_bicycle_url)


@functools.cache
def get_osrm_foot_client() -> BaseTravelTimeClient:
    return OsrmTravelTimeClient(settings.osrm_foot_url)


@functools.cache
def get_travel_time_service() -> TravelTimeService:
    return TravelTimeService(
        osrm_car_client=get_osrm_car_client(),
        osrm_bicycle_client=get_osrm_bicycle_client(),
        osrm_foot_client=get_osrm_foot_client(),
    )


@functools.cache
def get_planner_service() -> PlannerService:
    return PlannerService(
        travel_time_service=get_travel_time_service(),
    )
