from datetime import datetime

from pydantic import BaseModel


class EngineerOut(BaseModel):
    id: str
    start_point_lat: float
    start_point_lon: float
    shift_start: datetime
    shift_end: datetime


class RequestOut(BaseModel):
    id: int
    lat: float
    lon: float


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
    unassigned_request_ids: list[int]