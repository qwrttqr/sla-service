from datetime import datetime

from pydantic import BaseModel

from common.types import GeoPoint


class EngineerOut(BaseModel):
    id: str
    start_point_lat: float
    start_point_lon: float
    shift_start: datetime
    shift_end: datetime


class RequestOut(BaseModel):
    id: int
    point: GeoPoint


class UnassignedRequest(RequestOut):
    reason: str


class AssignmentOut(BaseModel):
    engineer_id: str
    request_id: int
    time_from: datetime
    time_to: datetime
    wait_minutes: int


class PlanResult(BaseModel):
    engineers: list[EngineerOut]
    requests: list[RequestOut]
    assignments: list[AssignmentOut]
    unassigned_requests: list[UnassignedRequest]
