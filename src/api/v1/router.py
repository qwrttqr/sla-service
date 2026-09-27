# api/v1/__init__.py  (or api/v1/router.py)
from fastapi import APIRouter

from api.v1.endpoints.generation import router as generation_router
from api.v1.endpoints.planning import router as planning_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(generation_router)
v1_router.include_router(planning_router)