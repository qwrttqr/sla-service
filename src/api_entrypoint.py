from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.router import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # TODO(sxtxri): сюда клиент редиса заедет

    yield


def create_app() -> FastAPI:
    app = FastAPI(title="SLA service", lifespan=lifespan)
    app.include_router(main_router)
    return app


app = create_app()
