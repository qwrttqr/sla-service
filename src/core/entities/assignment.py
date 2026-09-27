__all__ = ["Assignment", "UnassignedRequest", "Plan"]

from datetime import datetime

from pydantic import BaseModel

from common.types import EngineerId
from core.entities.request import Request


class Assignment(BaseModel):
    request_id: int
    engineer_id: EngineerId
    order: int  # position in engineer's route
    planned_arrival: datetime
    planned_start: datetime
    planned_finish: datetime
    wait_minutes: int
    travel_minutes: int  # TODO(sxtxri): в минутах?


class UnassignedRequest(BaseModel):
    request: Request
    reason: str


class Plan(BaseModel):
    assignments: list[Assignment]
    unassigned: list[UnassignedRequest]