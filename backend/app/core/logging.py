import logging
import json
import traceback
from datetime import datetime
from contextvars import ContextVar

# Context variable to hold the request ID for the current async execution context
request_id_ctx_var: ContextVar[str | None] = ContextVar("request_id", default=None)

class StructuredLogger(logging.Formatter):
    """
    A JSON formatter for structured logging.
    Emits log records as machine-readable JSON strings including runtime metadata.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "logger_name": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx_var.get(),
        }
        
        if record.exc_info:
            log_obj["exception"] = "".join(traceback.format_exception(*record.exc_info))
            
        # Add custom extra fields if they exist
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename",
                           "funcName", "levelname", "levelno", "lineno", "module",
                           "msecs", "message", "msg", "name", "pathname", "process",
                           "processName", "relativeCreated", "stack_info", "thread", "threadName"]:
                if key != "request_id":
                    log_obj[key] = value

        return json.dumps(log_obj)

def setup_structured_logging():
    """Configures the root logger to use the structured JSON formatter."""
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredLogger())
    
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Fastapi/Uvicorn specific overrides to prevent double logging or plain text
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.error").handlers = [handler]
