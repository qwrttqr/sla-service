from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.error_handlers import register_error_handlers
from api.routers import planning
from core.domain.engineer import VehicleType
from core.external.yandex_geocoder import YandexGeocoder
from core.services.data_processing.engineers import EngineerBuilder
from core.services.data_processing.requests import RequestBuilder
from core.services.geocoder import GeocoderService
from core.services.osrm_travel_time import OsrmTravelTime
from core.services.planner import Planner
from core.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # noinspection PyArgumentList
    settings = Settings()

    geocoder = GeocoderService(
        YandexGeocoder(settings.yandex_geocoder_api_key.get_secret_value())
    )

    travel_time_by_vehicle = {
        VehicleType.CAR: OsrmTravelTime(settings.osrm_car_url),
        VehicleType.BICYCLE: OsrmTravelTime(settings.osrm_bicycle_url),
        VehicleType.WALK: OsrmTravelTime(settings.osrm_foot_url),
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
    app.include_router(planning.router)
    register_error_handlers(app)
    return app


app = create_app()