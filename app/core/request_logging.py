"""Middleware for request IDs and request timing."""

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request

from app.core.logging_config import set_request_id

logger = logging.getLogger("marist_pedia.request")


def register_request_logging(app: FastAPI) -> None:
    """Add request logging middleware to the FastAPI application."""

    @app.middleware("http")
    async def request_logging_middleware(
        request: Request,
        call_next,
    ):
        request_id = str(uuid4())
        set_request_id(request_id)
        started = perf_counter()

        logger.info(
            "request_started method=%s path=%s",
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)
        except Exception:
            # The centralized exception handler will log the exception.
            logger.exception(
                "request_failed method=%s path=%s",
                request.method,
                request.url.path,
            )
            raise

        duration_ms = round((perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed method=%s path=%s status_code=%s duration_ms=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response
