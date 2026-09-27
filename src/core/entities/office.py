__all__ = ["Office"]

from pydantic import BaseModel
from common.types import GeoPoint


class Office(BaseModel):
    id: int
    address: str
    coords: GeoPoint
