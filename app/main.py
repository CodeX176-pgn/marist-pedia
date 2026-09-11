from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import (
    TrustedHostMiddleware,
)

from app.config.settings import settings
from app.core.database import init_database
from app.core.errors import register_error_handlers
from app.core.logging_config import configure_logging
from app.core.request_logging import (
    register_request_logging,
)
from app.routers import (
    admin,
    documents,
    health,
    quizzes,
    teacher,
)

# Configure logging before the server starts.
configure_logging()

# Make sure the database and its tables exist.
init_database()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,

    # Interactive API documentation can be disabled in production.
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)


# Add a request ID and request-duration logging.
register_request_logging(app)

# Register consistent application error responses.
register_error_handlers(app)


# Reject requests containing untrusted Host headers.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list,
)


# Restrict browser cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
    ],
    allow_headers=[
        "Accept",
        "Content-Type",
    ],
)


# Register application routes.
app.include_router(health.router)
app.include_router(quizzes.router)
app.include_router(documents.router)
app.include_router(admin.router)
app.include_router(teacher.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Return basic information about the application."""

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "message": "Welcome to Marist Pedia!",
    }