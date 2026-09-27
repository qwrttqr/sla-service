from pydantic import BaseModel


class GeocoderRequest(BaseModel):
    address: str


class GeocoderResponse(BaseModel):
    longitude: float
    latitude: float
