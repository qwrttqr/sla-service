import io
from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from api.dependencies import EngineerBuilderDep, PlannerDep, RequestBuilderDep
from core.entities.assignment import Assignment

plan_router = APIRouter(prefix="/plan", tags=["planning"])


class PlanResult(BaseModel):
    assignments: list[Assignment]
    unassigned_request_ids: list[int]


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
        assignments=plan.assignments,
        unassigned_request_ids=[u.request_id for u in plan.unassigned],
    )
