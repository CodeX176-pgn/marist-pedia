from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.core.errors import register_error_handlers
from app.routers import health, quizzes

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health.router,
    prefix=settings.api_prefix,
)

app.include_router(
    quizzes.router,
    prefix=settings.api_prefix,
)


register_error_handlers(app)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to Marist Pedia API",
        "version": settings.app_version,
    }
