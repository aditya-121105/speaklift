from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import engine

router = APIRouter()


@router.get("/")
def root():
    return {
        "message": "Welcome to SpeakLift API"
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@router.get("/db-health")
def db_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "connected"
    }