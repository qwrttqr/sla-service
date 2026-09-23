from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.error_handlers import register_error_handlers
from api.routers import planning
from core.domain.engineer import VehicleType
from core.external.yandex_geocoder import YandexGeocoder
from core.services.data_processing.engineers import EngineerBuilder
from core.services.data_processing.requests import RequestBuilder
from core.services.geocoder import GeocoderService
from core.services.osrm_travel_time import OsrmTravelTime, TrafficProfile
from core.services.planner import Planner
from core.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # noinspection PyArgumentList
    settings = Settings()

    geocoder = GeocoderService(
        YandexGeocoder(settings.yandex_geocoder_api_key.get_secret_value())
    )
    travel_time = OsrmTravelTime(
        urls={
            VehicleType.CAR: str(settings.osrm_car_url).rstrip("/"),
            VehicleType.BICYCLE: str(settings.osrm_bicycle_url).rstrip("/"),
            VehicleType.WALK: str(settings.osrm_foot_url).rstrip("/"),
        },
        traffic=TrafficProfile(settings.traffic_profile_path),
    )

    app.state.travel_time = travel_time
    app.state.planner = Planner(travel_time)
    app.state.engineer_builder = EngineerBuilder(geocoder=geocoder)
    app.state.request_builder = RequestBuilder(geocoder=geocoder)

    yield

    await travel_time.aclose()


def create_app() -> FastAPI:
    app = FastAPI(title="SLA service", lifespan=lifespan)
    app.include_router(planning.router)
    register_error_handlers(app)
    return app


app = create_app()