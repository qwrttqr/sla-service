from pydantic import BaseModel, Field
from enum import Enum
from datetime import time
from typing import Tuple

class VehicleType(str, Enum):
    CAR = "car"
    WALK = "walk"
    BICYCLE = "bicycle"
    PUBLIC_TRANSPORT = "public_transport"

class Skill(str, Enum):
    LOCAL = "local_works"
    CONNECTION = "connection_works"
    EMERGENCY = "emergency_works"

class Equipment(str, Enum):
    FMC = "FMC"
    FTTB = "FTTB"
    gigabit_connection = "gigabit_connection"


class Engineer(BaseModel):
    id: int
    starting_point_coords: Tuple[float, float]
    shift_start: time
    shift_end: time
    skills: set[Skill] = Field(..., min_length=1, max_length=3)
    vehicle_type: VehicleType
    equipment: set[Equipment]
