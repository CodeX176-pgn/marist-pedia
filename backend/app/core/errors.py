"""Centralized application error handling."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("marist_pedia.errors")


class AppError(Exception):
    """An expected application error with a safe client-facing message."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
    ) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def register_error_handlers(app: FastAPI) -> None:
    """Register all API-wide error handlers in one place."""

    @app.exception_handler(AppError)
    async def app_error_handler(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        # Expected application errors are logged without exposing internals.
        logger.warning(
            "application_error path=%s status_code=%s message=%s",
            request.url.path,
            exc.status_code,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"message": exc.message}},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        # FastAPI HTTP errors are normalized to the same predictable shape.
        logger.warning(
            "http_error path=%s status_code=%s detail=%s",
            request.url.path,
            exc.status_code,
            exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        # Invalid request data should return a useful 422 response.
        logger.warning(
            "validation_error path=%s errors=%s",
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        # Log the real exception for developers, but hide implementation details.
        logger.exception(
            "unhandled_exception path=%s error=%s",
            request.url.path,
            exc,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "An unexpected server error occurred."
                }
            },
        )
