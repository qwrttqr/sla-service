import io
from datetime import timezone
from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from api.dependencies import EngineerBuilderDep, PlannerDep, RequestBuilderDep
from api.v1.schemas.planning import EngineerOut, RequestOut, AssignmentOut, PlanResult

plan_router = APIRouter(prefix="/plan", tags=["planning"])

@plan_router.post("/csv", response_model=PlanResult)
async def build_plan_from_csv(
    engineers_file: Annotated[UploadFile, File()],
    requests_file: Annotated[UploadFile, File()],
    planner: PlannerDep,
    engineer_builder: EngineerBuilderDep,
    request_builder: RequestBuilderDep,
) -> PlanResult:
    engineers, offices = await engineer_builder.build_from_csv(
        io.BytesIO(await engineers_file.read())
    )
    requests = await request_builder.build_from_csv(
        io.BytesIO(await requests_file.read())
    )

    plan = await planner.build(engineers=engineers, offices=offices, requests=requests)

    return PlanResult(
        engineers=[
            EngineerOut(
                id=e.id,
                start_point_lat=e.starting_point_coords.lat,
                start_point_lon=e.starting_point_coords.lon,
                shift_start=e.shift_start,
                shift_end=e.shift_end,
            )
            for e in engineers
        ],
        requests=[
            RequestOut(id=r.id, lat=r.point_coords.lat, lon=r.point_coords.lon)
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
        unassigned_request_ids=[u.request_id for u in plan.unassigned],
    )
