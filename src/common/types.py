from enum import Enum
from typing import NamedTuple

Longitude = float
Latitude = float
EngineerId = str

class GeoPoint(NamedTuple):
    lon: Longitude
    lat: Latitude

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


class EventType(str, Enum):
    URGENT_REQUEST = "urgent_request"
    REQUEST_CANCELLATION = "request_cancellation"
    ENGINEER_UNAVAILABLE = "engineer_unavailable"
    PUBLIC_TRANSPORT = "public_transport"


class WorkType(str, Enum):
    CONNECT_CLIENT = "connect_client"
    EMERGENCY_WORK = "emergency_work"
    LOCAL_WORK_OR_REPAIR = "local_work_or_repair"
    POST_ORDER = "postorder"


class Status(str, Enum):
    SENT = "sent"
    ON_THE_WAY = "on_the_way"
    DONE = "done"
    CANCELLED = "cancelled"