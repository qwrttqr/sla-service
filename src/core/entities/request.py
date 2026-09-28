from datetime import datetime, timedelta

from pydantic import BaseModel, Field, computed_field

from common.types import (Equipment, GeoPoint, Skill, Status, VehicleType,
                          WorkType, District)

WORK_TYPE_DURATION_MAP: dict[WorkType, int] = {
    WorkType.CONNECT_CLIENT: 70,
    WorkType.EMERGENCY_WORK: 80,
    WorkType.POST_ORDER: 20,
    WorkType.LOCAL_WORK_OR_REPAIR: 30,
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
    point_coords: GeoPoint
    address: str
    work_type: WorkType
    request_start: datetime
    request_end: datetime
    required_vehicle_type: VehicleType | None = None
    required_equipment: set[Equipment] | None = None
    required_skills: set[Skill] = Field(..., min_length=1, max_length=3)
    district: District
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
    def arrive_before_to_accomplish(self) -> datetime:
        return self.request_end - timedelta(minutes=self.duration_minutes)
