from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_generate_quiz():
    response = client.post(
        "/api/quizzes/generate",
        json={
            "title": "Python Quiz",
            "chunks": [
                (
                    "Python is a high-level programming language "
                    "used for general-purpose programming."
                ),
                (
                    "FastAPI is a modern Python web framework "
                    "for building APIs."
                ),
            ],
            "question_count": 2,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["quiz"]["title"] == "Python Quiz"
    assert len(data["quiz"]["questions"]) == 2

    for question in data["quiz"]["questions"]:
        assert "correct_answer" not in question


def test_get_quizzes():
    response = client.get("/api/quizzes")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_missing_quiz():
    response = client.get(
        "/api/quizzes/does-not-exist"
    )

    assert response.status_code == 404
