from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.error_handlers import register_error_handlers
from api.v1.endpoints import generation, planning
from config import Settings
from api.v1.router import v1_router
from core.entities.engineer import VehicleType
from infra.clients.geocode.yandex import YandexGeoCodeClient
from core.services.data_processing.engineers import EngineerBuilder
from core.services.data_processing.requests import RequestBuilder
from core.services.geocoder import GeocoderService
from core.services.osrm_travel_time import TravelTimeService
from core.services.planner import Planner
from config import settings
from infra.clients.travel_time.osrm import OsrmTravelTimeClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    # noinspection PyArgumentList
    geocoder = GeocoderService(
        YandexGeoCodeClient(settings.yandex_geocoder_api_key.get_secret_value())
    )

    travel_time_by_vehicle = {
        VehicleType.CAR: TravelTimeService(OsrmTravelTimeClient(settings.osrm_car_url)),
        VehicleType.BICYCLE: TravelTimeService(OsrmTravelTimeClient(settings.osrm_bicycle_url)),
        VehicleType.WALK: TravelTimeService(OsrmTravelTimeClient(settings.osrm_foot_url)),
    }

    app.state.travel_time_by_vehicle = travel_time_by_vehicle
    app.state.planner = Planner(travel_time_by_vehicle)
    app.state.engineer_builder = EngineerBuilder(geocoder=geocoder)
    app.state.request_builder = RequestBuilder(geocoder=geocoder)

    yield

    for tt in travel_time_by_vehicle.values():
        await tt.aclose()


def create_app() -> FastAPI:
    app = FastAPI(title="SLA service", lifespan=lifespan)
    app.include_router(v1_router)
    register_error_handlers(app)
    return app


app = create_app()
