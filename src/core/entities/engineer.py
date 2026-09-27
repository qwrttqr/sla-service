__all__ = ["Engineer"]

from datetime import datetime

from pydantic import BaseModel, Field

from common.types import EngineerId, Equipment, GeoPoint, Skill, VehicleType, District


class Engineer(BaseModel):
    id: EngineerId
    name: str
    office_id: int
    office_name: str
    starting_point_coords: GeoPoint
    shift_start: datetime
    shift_end: datetime
    skills: set[Skill] = Field(..., min_length=1, max_length=3)
    vehicle_type: VehicleType
    districts: set[District]
    equipment: set[Equipment]
