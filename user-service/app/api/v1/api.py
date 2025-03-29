from fastapi import APIRouter

from app.api.v1.endpoints import user_profiles

api_router = APIRouter()
api_router.include_router(user_profiles.router, prefix="/profiles", tags=["user_profiles"])