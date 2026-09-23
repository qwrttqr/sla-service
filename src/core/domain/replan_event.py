from enum import Enum

from pydantic import BaseModel
from datetime import time

from core.domain.request import Request


class EventType(str, Enum):
    URGENT_REQUEST = "urgent_request"
    REQUEST_CANCELLATION = "request_cancellation"
    ENGINEER_UNAVAILABLE = "engineer_unavailable"
    PUBLIC_TRANSPORT = "public_transport"

class ReplanEvent(BaseModel):
    event_type: int
    happened_at: time
    request_id: int | None = None
    engineer_id: int | None = None
    new_request: Request | None = None