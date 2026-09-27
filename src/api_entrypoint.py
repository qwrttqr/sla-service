from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.error_handlers import register_error_handlers
from api.router import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # noinspection PyArgumentList

    # TODO(sxtxri): сюда клиент редиса заедет

    yield


def create_app() -> FastAPI:
    app = FastAPI(title="SLA service", lifespan=lifespan)
    app.include_router(main_router)
    register_error_handlers(app)
    return app


app = create_app()
