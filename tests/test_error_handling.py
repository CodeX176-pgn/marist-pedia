from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_validation_errors_have_consistent_shape() -> None:
    response = client.post(
        "/api/quizzes/generate",
        json={
            "title": "",
            "chunks": [],
            "question_count": 0,
        },
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)


def test_http_errors_keep_detail_shape() -> None:
    response = client.get("/api/quizzes/does-not-exist")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_unexpected_errors_are_not_exposed() -> None:
    @app.get("/test-error-handling-unexpected-error")
    def raise_unexpected_error() -> None:
        raise RuntimeError("database password should never be returned")

    isolated_client = TestClient(
        app,
        raise_server_exceptions=False,
    )
    response = isolated_client.get(
        "/test-error-handling-unexpected-error"
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "message": "An unexpected server error occurred."
        }
    }
    assert "database password" not in response.text


def test_request_id_header_is_present() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
