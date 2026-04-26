import logging
import os
import uuid
from contextvars import ContextVar
import traceback

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from infrastructure.settings.settings import settings


LOG_LEVEL = settings.log_level.upper() if settings.log_level else "INFO"


request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_context.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_context.reset(token)


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get() or "no-request-id"
        return True


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        filename = os.path.basename(record.pathname)
        request_id = getattr(record, "request_id", "no-request-id")
        message = record.getMessage()
        return (
            f"{self.formatTime(record, self.datefmt)} - "
            f"{record.levelname} - [{filename}:{record.lineno}] - "
            f"[ReqID:{request_id}] - {message} - "
            f"{str(record.exc_info[0]) + ': ' + str(record.exc_info[1]) if record.exc_info else ''}"
            f"{' - ' + str(traceback.format_tb(record.exc_info[2])) if record.exc_info and hasattr(record, 'traceback') else ''}"
        )


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": RequestIDFilter}},
    "formatters": {
        "default": {
            "()": ConsoleFormatter,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["request_id"],
        }
    },
    "root": {"level": LOG_LEVEL, "handlers": ["console"]},
}
