"""
Global exception handlers for the SpeakLift API.

All domain exceptions are converted to appropriate HTTP responses.
Generic exceptions are sanitized to avoid exposing internal details.
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException

from app.shared.exceptions import (
    SpeakLiftException,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ConflictError,
    AuthenticationError,
    InvalidSessionStateError,
    EvaluationError,
)

logger = logging.getLogger(__name__)


async def speaklift_exception_handler(
    request: Request,
    exc: SpeakLiftException,
) -> JSONResponse:
    """
    Handle all SpeakLift domain exceptions.

    Since all domain exceptions inherit from SpeakLiftException,
    this single handler can handle all of them by checking the
    concrete exception type and using its status_code and detail.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Never exposes stack traces in production.
    Logs the exception for debugging.
    Returns a sanitized HTTP 500 response.
    """
    # Do not handle FastAPI's built-in exceptions
    if isinstance(exc, (HTTPException, RequestValidationError)):
        # Let FastAPI handle these
        raise exc

    logger.exception(
        f"Unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers.

    This function should be called from main.py to set up
    centralized exception handling for the entire application.
    """
    # Register handler for all SpeakLift domain exceptions
    app.add_exception_handler(SpeakLiftException, speaklift_exception_handler)
    
    # Register handler for unexpected exceptions
    app.add_exception_handler(Exception, generic_exception_handler)