import io
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from src.api.dependencies import PlannerDep, EngineerBuilderDep, RequestBuilderDep
from src.core.domain.assignment import Assignment

router = APIRouter(prefix="/plan", tags=["planning"])


class PlanResult(BaseModel):
    assignments: list[Assignment]
    unassigned_request_ids: list[int]


@router.post("/csv", response_model=PlanResult)
async def build_plan_from_csv(
    engineers_file: Annotated[UploadFile, File()],
    requests_file: Annotated[UploadFile, File()],
    planner: PlannerDep,
    engineer_builder: EngineerBuilderDep,
    request_builder: RequestBuilderDep,
) -> PlanResult:
    engineers = await engineer_builder.build_from_csv(io.BytesIO(await engineers_file.read()))
    requests = await request_builder.build_from_csv(io.BytesIO(await requests_file.read()))

    return await run_in_threadpool(
        planner.build, engineers=engineers, requests=requests
    )