from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check() -> dict[str, str]:
    """Check whether the application process is alive."""

    return {
        "status": "ok",
        "service": "Marist Pedia",
    }


@router.get("/ready")
def readiness_check(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Check whether the application can access its database."""

    # A very small query verifies that the database is usable.
    db.execute(text("SELECT 1"))

    return {
        "status": "ready",
        "service": "Marist Pedia",
        "database": "ok",
    }