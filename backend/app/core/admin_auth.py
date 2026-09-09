import secrets

from fastapi import Header, HTTPException, status

from app.config.settings import settings


def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
    """Require the configured teacher/admin key for protected routes."""
    if not x_admin_key or not secrets.compare_digest(
        x_admin_key,
        settings.admin_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid teacher/admin key is required.",
        )
