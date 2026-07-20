import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import status
from app.core.config import settings
from app.core.exception_handlers import build_error_response

logger = logging.getLogger(__name__)

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Rejects requests whose Content-Length exceeds the configured maximum size.
    """
    async def dispatch(self, request: Request, call_next):
        content_length_str = request.headers.get("content-length")
        
        if content_length_str:
            try:
                content_length = int(content_length_str)
                if content_length > settings.MAX_REQUEST_SIZE_BYTES:
                    logger.warning(
                        "Payload too large",
                        extra={"content_length": content_length, "limit": settings.MAX_REQUEST_SIZE_BYTES}
                    )
                    return build_error_response(
                        request,
                        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        "PAYLOAD_TOO_LARGE",
                        f"Request payload size {content_length} bytes exceeds the maximum allowed size of {settings.MAX_REQUEST_SIZE_BYTES} bytes."
                    )
            except ValueError:
                pass # Invalid content-length header, allow parsing to fail naturally
                
        return await call_next(request)
