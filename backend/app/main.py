import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.exception_handlers import register_exception_handlers

from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_structured_logging
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.size_limit import RequestSizeLimitMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.db.session import engine

# Configure logging natively
setup_structured_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup validation
    logger.info("Starting SpeakLift API...")
    try:
        settings.validate_configuration()
        logger.info(f"Configuration validated. Environment: {settings.LLM_ROUTING_STRATEGY}")
    except Exception as e:
        logger.critical(f"Configuration validation failed: {str(e)}")
        raise e
        
    yield
    
    # Graceful shutdown
    logger.info("Initiating graceful shutdown...")
    engine.dispose()
    logger.info("Database connections disposed.")

app = FastAPI(
    title="SpeakLift API",
    description="AI-Powered Interview & Viva Confidence Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Add built-in Middlewares first (outermost)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add custom Middlewares (ordered)
app.add_middleware(CorrelationIdMiddleware) # Provides request ID for logging
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include API router
app.include_router(api_router)

# Register global exception handlers
register_exception_handlers(app)