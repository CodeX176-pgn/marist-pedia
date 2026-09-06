from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Marist Pedia",
    description="Document-powered quiz application",
    version="0.1.0",
)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/")
async def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "Marist Pedia backend is running!",
    }
