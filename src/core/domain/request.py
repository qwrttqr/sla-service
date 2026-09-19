from datetime import datetime
from enum import Enum
from typing import Tuple

from pydantic import BaseModel, computed_field

from src.core.domain.engineer import Skill, VehicleType, Equipment


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


WORK_TYPE_DURATION_MAP: dict[WorkType, int] = {
    WorkType.CONNECT_CLIENT: 90,
    WorkType.EMERGENCY_WORK: 100,
    WorkType.POST_ORDER: 40,
    WorkType.LOCAL_WORK_OR_REPAIR: 50,
}

WORK_TYPE_PRIORITY_MAP: dict[WorkType, int] = {
    WorkType.EMERGENCY_WORK: 1,
    WorkType.CONNECT_CLIENT: 2,
    WorkType.POST_ORDER: 3,
    WorkType.LOCAL_WORK_OR_REPAIR: 3,
}

WORK_TYPE_SKILL_MAP: dict[WorkType, Skill] = {
    WorkType.CONNECT_CLIENT: Skill.CONNECTION_WORKS,
    WorkType.EMERGENCY_WORK: Skill.EMERGENCY_WORKS,
    WorkType.LOCAL_WORK_OR_REPAIR: Skill.LOCAL_WORKS,
    WorkType.POST_ORDER: Skill.LOCAL_WORKS,
}


class Request(BaseModel):
    id: int
    point_coords: Tuple[float, float]
    work_type: WorkType
    request_start: datetime
    request_end: datetime
    required_vehicle_type: VehicleType | None = None
    required_equipment: Equipment | None = None
    status: Status

    @computed_field
    @property
    def duration_minutes(self) -> int:
        return int(WORK_TYPE_DURATION_MAP[self.work_type])

    @computed_field
    @property
    def priority(self) -> int:
        return WORK_TYPE_PRIORITY_MAP[self.work_type]

    @computed_field
    @property
    def required_skills(self) -> set[Skill]:
        return {WORK_TYPE_SKILL_MAP[self.work_type]}
