from typing import Annotated

from fastapi import Depends, Request

from core.services.data_processing.engineers import EngineerBuilder
from core.services.data_processing.requests import RequestBuilder
from src.core.services.planner import Planner


def get_planner(request: Request) -> Planner:
    return request.app.state.planner


def get_engineer_builder(request: Request) -> EngineerBuilder:
    return request.app.state.engineer_builder


def get_request_builder(request: Request) -> EngineerBuilder:
    return request.app.state.request_builder


PlannerDep = Annotated[Planner, Depends(get_planner)]
EngineerBuilderDep = Annotated[EngineerBuilder, Depends(get_engineer_builder)]
RequestBuilderDep = Annotated[RequestBuilder, Depends(get_request_builder)]
