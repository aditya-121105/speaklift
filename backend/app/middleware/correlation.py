import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import request_id_ctx_var

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject a unique correlation ID into every request.
    This ID is stored in a context variable for logging and added as a response header.
    Also tracks request duration.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # Check if the client provided an X-Request-ID; otherwise generate a new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set the context variable for structured logging
        token = request_id_ctx_var.set(request_id)
        
        start_time = time.time()
        try:
            response = await call_next(request)
            
            # Add execution duration to response headers
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Inject correlation ID into response headers
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Clean up the context variable
            request_id_ctx_var.reset(token)
