import logging
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.exception_handlers import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="SpeakLift API",
    description="AI-Powered Interview & Viva Confidence Platform",
    version="1.0.0",
)

# Include API router
app.include_router(api_router)

# Register global exception handlers
register_exception_handlers(app)