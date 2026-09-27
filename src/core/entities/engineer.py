__all__ = ["Engineer"]

from pydantic import BaseModel, Field
from datetime import datetime
from common.types import Skill, VehicleType, Equipment, GeoPoint


class Engineer(BaseModel):
    id: int
    office_id: int
    starting_point_coords: GeoPoint
    shift_start: datetime
    shift_end: datetime
    skills: set[Skill] = Field(..., min_length=1, max_length=3)
    vehicle_type: VehicleType
    equipment: set[Equipment]
