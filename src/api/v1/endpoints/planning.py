import io
from datetime import timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from api.v1.schemas.planning import EngineerOut, RequestOut, AssignmentOut, PlanResult, UnassignedRequest
from common.types import GeoPoint
from core.bootstrap import (get_engineer_builder, get_planner_service,
                            get_request_builder)
from core.services.data_processing.engineers import EngineerBuilder
from core.services.data_processing.requests import RequestBuilder
from core.services.planner import PlannerService

plan_router = APIRouter(prefix="/plan", tags=["planning"])


# TODO(sxtxri): одну для всех базовую модельку бы намутить, она бы еще кейс написания задавала


@plan_router.post("/csv", response_model=PlanResult)
async def build_plan_from_csv(
        engineers_file: Annotated[UploadFile, File()],
        requests_file: Annotated[UploadFile, File()],
        planner_service: Annotated[PlannerService, Depends(get_planner_service)],
        engineer_builder: Annotated[EngineerBuilder, Depends(get_engineer_builder)],
        request_builder: Annotated[RequestBuilder, Depends(get_request_builder)],
) -> PlanResult:
    engineers, offices = await engineer_builder.build_from_csv(
        io.BytesIO(await engineers_file.read())
    )
    requests = await request_builder.build_from_csv(
        io.BytesIO(await requests_file.read())
    )

    plan = await planner_service.build(
        engineers=engineers, offices=offices, requests=requests
    )

    return PlanResult(
        engineers=[
            EngineerOut(
                id=e.id,
                name=e.name,
                vehicle=e.vehicle_type.value,
                office=e.office_name,
                start_point_lat=e.starting_point_coords.lat,
                start_point_lon=e.starting_point_coords.lon,
                shift_start=e.shift_start,
                shift_end=e.shift_end,
            )
            for e in engineers
        ],
        requests=[
            RequestOut(id=r.id, point=r.point_coords)
            for r in requests
        ],
        assignments=[
            AssignmentOut(
                engineer_id=a.engineer_id,
                request_id=a.request_id,
                time_from=a.planned_start.astimezone(timezone.utc),  # actual work start, not arrival
                time_to=a.planned_finish.astimezone(timezone.utc),
                wait_minutes=a.wait_minutes,
            )
            for a in plan.assignments
        ],
        unassigned_requests=[UnassignedRequest(id=u.request_id, reason=u.reason, point=u.point)
                             for u in plan.unassigned],
    )
