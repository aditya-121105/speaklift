import logging
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from app.shared.exceptions import SpeakLiftException
from app.core.logging import request_id_ctx_var

logger = logging.getLogger(__name__)

def build_error_response(request: Request, status_code: int, error_code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "request_id": request_id_ctx_var.get() or "unknown",
                "error_code": error_code,
                "message": message,
                "path": request.url.path,
                "status": status_code,
            }
        }
    )

async def speaklift_exception_handler(request: Request, exc: SpeakLiftException) -> JSONResponse:
    logger.warning(
        f"Domain exception: {exc.detail}",
        extra={"error_code": exc.__class__.__name__, "path": request.url.path}
    )
    return build_error_response(
        request, 
        exc.status_code, 
        exc.__class__.__name__, 
        exc.detail
    )

async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"error_code": "VALIDATION_ERROR", "path": request.url.path}
    )
    return build_error_response(
        request, 
        status.HTTP_422_UNPROCESSABLE_ENTITY, 
        "VALIDATION_ERROR", 
        "Invalid request parameters or body."
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        f"HTTP exception: {exc.detail}",
        extra={"error_code": "HTTP_ERROR", "path": request.url.path}
    )
    return build_error_response(
        request, 
        exc.status_code, 
        "HTTP_ERROR", 
        str(exc.detail)
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        f"Unhandled exception: {exc}",
        extra={"path": request.url.path, "method": request.method}
    )
    return build_error_response(
        request, 
        status.HTTP_500_INTERNAL_SERVER_ERROR, 
        "INTERNAL_SERVER_ERROR", 
        "An unexpected error occurred."
    )

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(SpeakLiftException, speaklift_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)