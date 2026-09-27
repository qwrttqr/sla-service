__all__ = ["Engineer"]

from datetime import datetime

from pydantic import BaseModel, Field

from common.types import Equipment, GeoPoint, Skill, VehicleType


class Engineer(BaseModel):
    id: EngineerId
    office_id: int
    starting_point_coords: GeoPoint
    shift_start: datetime
    shift_end: datetime
    skills: set[Skill] = Field(..., min_length=1, max_length=3)
    vehicle_type: VehicleType
    equipment: set[Equipment]
