import io
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from core.bootstrap import (get_engineer_builder, get_planner_service,
                            get_request_builder)
from core.entities.assignment import Assignment
from core.services.data_processing.engineers import EngineerBuilder
from core.services.data_processing.requests import RequestBuilder
from core.services.planner import PlannerService

plan_router = APIRouter(prefix="/plan", tags=["planning"])


# TODO(sxtxri): одну для всех базовую модельку бы намутить, она бы еще кейс написания задавала
class PlanResult(BaseModel):
    assignments: list[Assignment]
    unassigned_request_ids: list[int]


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
        assignments=plan.assignments,
        unassigned_request_ids=[u.request_id for u in plan.unassigned],
    )
