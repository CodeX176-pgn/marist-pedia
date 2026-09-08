"""Application logging configuration.

This module keeps logging setup in one place so every part of the API
uses the same format and log level.
"""

import json
import logging
import time
from contextvars import ContextVar

# Stores the request ID for the request currently being handled.
_request_id: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    """Write log records as simple JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        # Keep log output machine-readable while still being easy to read.
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": _request_id.get(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    """Configure application logging once when the API starts."""

    logger = logging.getLogger("marist_pedia")

    # Avoid adding duplicate handlers when tests or reloads initialize the app.
    if logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z"))

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def set_request_id(request_id: str) -> None:
    """Make a request ID available to all logs for the current request."""

    _request_id.set(request_id)


