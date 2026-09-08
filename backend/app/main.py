from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config.settings import settings
from app.routers import documents, health, quizzes

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


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
    allow_methods=["GET", "POST"],
    allow_headers=["Accept", "Content-Type"],
)


app.include_router(health.router)
app.include_router(quizzes.router)
app.include_router(documents.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "message": "Welcome to Marist Pedia!",
    }
