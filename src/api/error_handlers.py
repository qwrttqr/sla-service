from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions.geocoder_failure import GeocoderFailure


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(GeocoderFailure)
    async def geocoder_failure_handler(_: Request, exc: GeocoderFailure):
        return JSONResponse(status_code=502, content={"detail": f"Geocoding failed: {exc}"})