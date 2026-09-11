from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
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

# Create a factory that produces short-lived database sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def _run_lightweight_migrations() -> None:
    """Add small schema changes to databases created by older phases."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "quizzes" not in tables:
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("quizzes")
    }

    # Phase I adds publication state and an edit timestamp.
    with engine.begin() as connection:
        if "is_published" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE quizzes "
                    "ADD COLUMN is_published BOOLEAN NOT NULL DEFAULT 1"
                )
            )

        if "updated_at" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE quizzes "
                    "ADD COLUMN updated_at DATETIME"
                )
            )
            connection.execute(
                text(
                    "UPDATE quizzes SET updated_at = created_at "
                    "WHERE updated_at IS NULL"
                )
            )


def init_database() -> None:
    """Create tables and apply small upgrades when the app starts."""
    if settings.database_url.startswith("sqlite"):
        Path(settings.database_file).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    # Create tables that don't already exist.
    Base.metadata.create_all(bind=engine)

    # Upgrade databases produced by earlier project phases.
    _run_lightweight_migrations()


def get_db() -> Generator[Session]:
    """Provide a database session and close it afterwards."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
