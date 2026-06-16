from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="SpeakLift API",
    description="AI-Powered Interview & Viva Confidence Platform",
    version="1.0.0",
)

app.include_router(api_router)