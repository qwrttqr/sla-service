from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class VehicleType(str, Enum):
    CAR = "car"
    WALK = "walk"
    BICYCLE = "bicycle"
    PUBLIC_TRANSPORT = "public_transport"


class Skill(str, Enum):
    LOCAL_WORKS = "local_works"
    CONNECTION_WORKS = "connection_works"
    EMERGENCY_WORKS = "emergency_works"


class Equipment(str, Enum):
    FMC = "FMC"
    FTTB = "FTTB"
    gigabit_connection = "gigabit_connection"


class Engineer(BaseModel):
    id: int
    office_id: int
    starting_point_coords: tuple[float, float]
    shift_start: datetime
    shift_end: datetime
    skills: set[Skill] = Field(..., min_length=1, max_length=3)
    vehicle_type: VehicleType
    equipment: set[Equipment]
