from app.config.settings import settings
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def admin_headers() -> dict[str, str]:
    return {"X-Admin-Key": settings.admin_key}


def generate_quiz() -> dict:
    response = client.post(
        "/api/quizzes/generate",
        json={
            "title": "Teacher Review Quiz",
            "chunks": ["Python is a programming language."],
            "question_count": 1,
        },
    )
    assert response.status_code == 201
    return response.json()["quiz"]


def test_admin_requires_key() -> None:
    response = client.get("/api/admin/quizzes")
    assert response.status_code == 401


def test_admin_can_list_and_publish_quiz() -> None:
    quiz = generate_quiz()

    response = client.get("/api/admin/quizzes", headers=admin_headers())
    assert response.status_code == 200
    assert response.json()[0]["is_published"] is False

    response = client.put(
        f"/api/admin/quizzes/{quiz['id']}",
        headers=admin_headers(),
        json={
            "title": "Reviewed Python Quiz",
            "description": "Approved by a teacher.",
            "is_published": True,
        },
    )
    assert response.status_code == 200

    public = client.get("/api/quizzes")
    assert any(item["id"] == quiz["id"] for item in public.json())


def test_admin_can_edit_question() -> None:
    quiz = generate_quiz()
    question = quiz["questions"][0]

    response = client.put(
        f"/api/admin/quizzes/{quiz['id']}/questions/{question['id']}",
        headers=admin_headers(),
        json={
            "text": "What is Python?",
            "choices": [
                {"id": "A", "text": "A programming language"},
                {"id": "B", "text": "A database"},
            ],
            "correct_answer": "A",
            "explanation": "Python is a programming language.",
            "difficulty": "easy",
        },
    )
    assert response.status_code == 200

    reviewed = client.get(
        f"/api/admin/quizzes/{quiz['id']}",
        headers=admin_headers(),
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["questions"][0]["text"] == "What is Python?"
