from typing import Annotated

from fastapi import Depends, Request

from core.services.data_processing.engineers import EngineerBuilder
from core.services.data_processing.requests import RequestBuilder
from core.services.planner import Planner
from core.clients.travel_time.base_client import BaseTravelTimeClient


def get_planner(request: Request) -> Planner:
    return request.app.state.planner


def get_travel_time(request: Request) -> BaseTravelTimeClient:
    return request.app.state.travel_time


def get_engineer_builder(request: Request) -> EngineerBuilder:
    return request.app.state.engineer_builder


def get_request_builder(request: Request) -> RequestBuilder:
    return request.app.state.request_builder


PlannerDep = Annotated[Planner, Depends(get_planner)]
TravelTimeDep = Annotated[BaseTravelTimeClient, Depends(get_travel_time)]
EngineerBuilderDep = Annotated[EngineerBuilder, Depends(get_engineer_builder)]
RequestBuilderDep = Annotated[RequestBuilder, Depends(get_request_builder)]
