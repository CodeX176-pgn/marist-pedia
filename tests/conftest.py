from collections.abc import Iterator

import pytest

from app.config.settings import settings
from app.routers.documents import router as document_router
from app.routers.quizzes import quiz_service, session_service


@pytest.fixture(autouse=True)
def isolate_test_state() -> Iterator[None]:
    """Keep in-memory services and uploaded test files isolated."""

    # Clear data created by previous tests so test order does not matter.
    quiz_service._quizzes.clear()
    session_service._sessions.clear()

    existing_files = set(settings.upload_directory.iterdir())

    yield

    # Remove only files created by this test; keep pre-existing uploads safe.
    for path in settings.upload_directory.iterdir():
        if path not in existing_files and path.is_file():
            path.unlink(missing_ok=True)
