from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings
from app.models.database import Base

# SQLite normally restricts a connection to one thread.
# FastAPI can use multiple threads, so we disable that restriction.
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)


# Create the SQLAlchemy database engine.
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)


# Create a factory that produces database sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def init_database() -> None:
    """Create database tables when the application starts."""

    # Make sure the SQLite storage folder exists.
    if settings.database_url.startswith("sqlite"):
        Path(settings.database_file).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    # Create tables that don't already exist.
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session]:
    """Provide a database session and close it afterwards."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
