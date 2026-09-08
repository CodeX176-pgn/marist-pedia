from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_complete_quiz_api_flow() -> None:
    """Verify generation, sessions, answers, and final evaluation together."""

    generated = client.post(
        "/api/quizzes/generate",
        json={
            "title": "Python Quiz",
            "chunks": [
                "Python is a programming language.",
                "FastAPI is a Python web framework.",
            ],
            "question_count": 2,
        },
    )

    assert generated.status_code == 201
    quiz = generated.json()["quiz"]
    quiz_id = quiz["id"]

    session_response = client.post(
        f"/api/quizzes/{quiz_id}/sessions",
        json={"quiz_id": quiz_id},
    )

    assert session_response.status_code == 201
    session = session_response.json()
    session_id = session["id"]
    assert session["question_order"]

    for question_id in session["question_order"]:
        answer_response = client.post(
            f"/api/quizzes/sessions/{session_id}/answers",
            json={
                "question_id": question_id,
                "selected_answer": "A",
            },
        )
        assert answer_response.status_code == 200

    result_response = client.post(
        f"/api/quizzes/sessions/{session_id}/submit"
    )

    assert result_response.status_code == 200
    result = result_response.json()
    assert result["session_id"] == session_id
    assert result["quiz_id"] == quiz_id
    assert result["total_questions"] == 2
    assert result["score"] == 2
    assert result["percentage"] == 100.0


def test_quiz_api_rejects_invalid_answer() -> None:
    """Verify invalid answer choices are rejected at the API boundary."""

    generated = client.post(
        "/api/quizzes/generate",
        json={
            "title": "Validation Quiz",
            "chunks": ["Python is a programming language."],
            "question_count": 1,
        },
    )
    quiz_id = generated.json()["quiz"]["id"]

    session = client.post(
        f"/api/quizzes/{quiz_id}/sessions",
        json={"quiz_id": quiz_id},
    ).json()

    response = client.post(
        f"/api/quizzes/sessions/{session['id']}/answers",
        json={
            "question_id": session["question_order"][0],
            "selected_answer": "Z",
        },
    )

    assert response.status_code == 400
    assert "Invalid answer choice" in response.json()["detail"]
