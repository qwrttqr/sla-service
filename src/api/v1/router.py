from fastapi import APIRouter

from api.v1.endpoints.generation import generation_router
from api.v1.endpoints.planning import plan_router

# api v1 routers
api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(generation_router)
api_v1_router.include_router(plan_router)
