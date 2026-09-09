# This test checks that the teacher router is registered
# and returns the expected response.

from app.main import app
from fastapi.testclient import TestClient

# TestClient allows us to test FastAPI without starting
# a real Uvicorn server.
client = TestClient(app)


def test_teacher_status():
    """Verify that the teacher API is available."""

    response = client.get("/api/teacher/status")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "area": "teacher",
    }
