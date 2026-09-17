from pydantic import BaseModel, Field
from datetime import time
from typing import Tuple

from core.domain.engineer import Skill, VehicleType, Equipment


class Request(BaseModel):
    id: int
    point_coords: Tuple[float, float]
    duration_minutes: int
    request_start: time
    request_end: time
    required_skills: set[Skill] = Field(..., min_length=1, max_length=3)
    required_vehicle_type: VehicleType | None
    required_equipment: Equipment | None