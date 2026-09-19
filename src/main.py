import os

from dotenv import load_dotenv

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.services.data_processing.engineers import EngineerBuilder
from src.core.services.data_processing.requests import RequestBuilder
from src.api.error_handlers import register_error_handlers
from src.api.routers import planning
from src.core.external.yandex_geocoder import YandexGeocoder
from src.core.services.geocoder import GeocoderService
from src.core.services.planner import Planner


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    geocoder = GeocoderService(YandexGeocoder(str(os.getenv("YANDEX_GEOCODER_API_KEY"))))
    app.state.planner = Planner(geocoder=geocoder)
    app.state.engineer_builder = EngineerBuilder(geocoder=geocoder)
    app.state.request_builder = RequestBuilder(geocoder=geocoder)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="SLA service", lifespan=lifespan)
    app.include_router(planning.router)
    register_error_handlers(app)
    return app


app = create_app()
