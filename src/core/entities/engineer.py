__all__ = ["Engineer"]

from pydantic import BaseModel, Field
from datetime import datetime
from common.types import Skill, VehicleType, Equipment, EngineerId


class Engineer(BaseModel):
    id: EngineerId
    office_id: int
    starting_point_coords: tuple[float, float]
    shift_start: datetime
    shift_end: datetime
    skills: set[Skill] = Field(..., min_length=1, max_length=3)
    vehicle_type: VehicleType
    equipment: set[Equipment]
