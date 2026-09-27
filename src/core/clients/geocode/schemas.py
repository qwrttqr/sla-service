from pydantic import BaseModel

from common.types import GeoPoint


class GeocoderRequest(BaseModel):
    address: str


class GeocoderResponse(BaseModel):
    point: GeoPoint
