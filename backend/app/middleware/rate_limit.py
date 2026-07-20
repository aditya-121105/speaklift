import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import status
from app.core.config import settings
from app.core.exception_handlers import build_error_response

logger = logging.getLogger(__name__)

# Basic in-memory fixed-window rate limiter
# Future enhancement: Replace with Redis-based implementation
_rate_limits: dict[str, list[float]] = defaultdict(list)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Implements IP-based rate limiting.
    Limits clients to RATE_LIMIT_PER_MINUTE requests per minute.
    """
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean up requests older than 1 minute
        history = _rate_limits[client_ip]
        history = [ts for ts in history if now - ts < 60]
        
        if len(history) >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(
                "Rate limit exceeded",
                extra={"client_ip": client_ip, "limit": settings.RATE_LIMIT_PER_MINUTE}
            )
            
            # Calculate retry after
            oldest_request = history[0] if history else now
            retry_after = max(1, int(60 - (now - oldest_request)))
            
            response = build_error_response(
                request,
                status.HTTP_429_TOO_MANY_REQUESTS,
                "RATE_LIMIT_EXCEEDED",
                f"Rate limit of {settings.RATE_LIMIT_PER_MINUTE} requests per minute exceeded."
            )
            response.headers["Retry-After"] = str(retry_after)
            return response
            
        history.append(now)
        _rate_limits[client_ip] = history
        
        return await call_next(request)
