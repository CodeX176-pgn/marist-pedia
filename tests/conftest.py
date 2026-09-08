import os
from collections.abc import Iterator

import pytest

# Tests must NEVER modify the real application database.
os.environ["DATABASE_URL"] = (
    "sqlite:///storage/test_marist_pedia.db"
)


from app.config.settings import settings
from app.core.database import engine
from app.models.database import Base


@pytest.fixture(autouse=True)
def isolate_test_state() -> Iterator[None]:
    """Keep database rows and uploads isolated per test."""

    # Start each test with a completely clean database.
    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )

    settings.upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing_files = set(
        settings.upload_directory.iterdir()
    )

    yield

    # Reset the test database after the test.
    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )

    # Remove only files created by the test.
    for path in settings.upload_directory.iterdir():
        if (
            path not in existing_files
            and path.is_file()
        ):
            path.unlink(
                missing_ok=True
            )