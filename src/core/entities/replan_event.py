__all__ = ["ReplanEvent"]

from datetime import time

from pydantic import BaseModel

from common.types import EngineerId
from core.entities.request import Request


class ReplanEvent(BaseModel):
    event_type: int
    happened_at: time
    request_id: int | None = None
    engineer_id: EngineerId | None = None
    new_request: Request | None = None
