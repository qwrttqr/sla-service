__all__ = ["ReplanEvent"]

from pydantic import BaseModel
from datetime import time

from core.entities.request import Request
from common.types import EngineerId

class ReplanEvent(BaseModel):
    event_type: int
    happened_at: time
    request_id: int | None = None
    engineer_id: EngineerId | None = None
    new_request: Request | None = None