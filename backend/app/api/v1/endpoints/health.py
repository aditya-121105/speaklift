import time
import os
import platform
from fastapi import APIRouter, Response, status
from sqlalchemy import text
from app.db.session import engine
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter(tags=["Health"])

START_TIME = time.time()

class Diagnostics(BaseModel):
    app_name: str
    version: str
    uptime_seconds: float
    environment: str
    python_version: str

class LiveResponse(BaseModel):
    status: str
    diagnostics: Diagnostics

class ReadyResponse(BaseModel):
    status: str
    database: str
    llm_provider: str
    diagnostics: Diagnostics

def _get_diagnostics() -> Diagnostics:
    return Diagnostics(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        uptime_seconds=round(time.time() - START_TIME, 2),
        environment=os.getenv("ENV", "development"),
        python_version=platform.python_version()
    )

@router.get("/health/live", response_model=LiveResponse)
def liveness_probe():
    """Liveness probe to check if the application process is running."""
    return LiveResponse(
        status="alive",
        diagnostics=_get_diagnostics()
    )

@router.get("/health/ready", response_model=ReadyResponse)
def readiness_probe(response: Response):
    """Readiness probe to check if the application can serve traffic."""
    db_status = "connected"
    overall_status = "ready"
    
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        overall_status = "not_ready"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadyResponse(
        status=overall_status,
        database=db_status,
        llm_provider=settings.LLM_DEFAULT_PROVIDER,
        diagnostics=_get_diagnostics()
    )