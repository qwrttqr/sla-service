from datetime import time

from pydantic import BaseModel


class Assignment(BaseModel):
    request_id: int
    engineer_id: int
    order: int              # position in engineer's route
    planned_arrival: time
    travel_minutes: int

class Plan(BaseModel):
    assignments: list[Assignment]
    unassigned: list["UnassignedRequest"]

class UnassignedRequest(BaseModel):
    request_id: int
    reason: str