from pydantic import BaseModel

from common.types import GeoPoint

class TravelTimeRequest(BaseModel):
    origins: list[GeoPoint]
    destinations: list[GeoPoint]
    profile: str


class TravelTimeResponse(BaseModel):
    durations_minutes: list[list[float | None]]