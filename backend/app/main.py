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


# Configure application logging before the server starts.
configure_logging()

# Make sure the database exists before the API starts.
init_database()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


# Give every request a traceable ID and log its duration.
register_request_logging(app)

# Handle expected and unexpected API errors consistently.
register_error_handlers(app)


# Reject requests using untrusted Host headers.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list,
)


# Restrict browser-based cross-origin requests.
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


# Register the application's API routers.
app.include_router(health.router)
app.include_router(quizzes.router)
app.include_router(documents.router)
app.include_router(admin.router)

# Register the teacher status/teacher-area router.
app.include_router(teacher.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Return basic information about the application."""

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "message": "Welcome to Marist Pedia!",
    }

