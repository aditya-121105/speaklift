from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.interview_sessions import (
    router as interview_router,
)
from app.api.v1.endpoints.resumes import router as resumes_router
from app.api.v1.endpoints.job_descriptions import router as job_descriptions_router

api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(interview_router)
api_router.include_router(resumes_router)
api_router.include_router(job_descriptions_router)