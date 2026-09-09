from fastapi.testclient import TestClient
from sqlalchemy import update

from app.core.database import SessionLocal
from app.main import app
from app.models.database import QuizRecord


# TestClient allows us to test the FastAPI application
# without starting a separate Uvicorn server.
client = TestClient(app)


def publish_quiz(quiz_id: str) -> None:
    """
    Publish a generated quiz for the integration test.

    In the real application, a teacher performs this action
    through the teacher/admin workflow. The test changes the
    database directly so this test can focus on the quiz API.
    """

    db = SessionLocal()

    try:
        db.execute(
            update(QuizRecord)
            .where(
                QuizRecord.id == quiz_id,
            )
            .values(
                is_published=True,
            )
        )

        db.commit()

    finally:
        db.close()


def test_complete_quiz_api_flow() -> None:
    """
    Verify generation, publication, sessions, answers,
    and final evaluation together.
    """

    # Generate a new quiz.
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

    # Generated quizzes are drafts.
    # Publish the quiz before testing the student workflow.
    publish_quiz(quiz_id)

    # Start a student attempt.
    session_response = client.post(
        f"/api/quizzes/{quiz_id}/sessions",
        json={
            "quiz_id": quiz_id,
        },
    )

    assert session_response.status_code == 201

    session = session_response.json()
    session_id = session["id"]

    assert session["question_order"]

    # Answer every question.
    for question_id in session["question_order"]:
        answer_response = client.post(
            f"/api/quizzes/sessions/{session_id}/answers",
            json={
                "question_id": question_id,
                "selected_answer": "A",
            },
        )

        assert answer_response.status_code == 200

    # Submit the completed quiz.
    result_response = client.post(
        f"/api/quizzes/sessions/{session_id}/submit",
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

    # Generate a quiz.
    generated = client.post(
        "/api/quizzes/generate",
        json={
            "title": "Validation Quiz",
            "chunks": [
                "Python is a programming language.",
            ],
            "question_count": 1,
        },
    )

    assert generated.status_code == 201

    quiz_id = generated.json()["quiz"]["id"]

    # Publish the draft before starting a student attempt.
    publish_quiz(quiz_id)

    # Start the student session.
    session_response = client.post(
        f"/api/quizzes/{quiz_id}/sessions",
        json={
            "quiz_id": quiz_id,
        },
    )

    assert session_response.status_code == 201

    session = session_response.json()

    # Try to submit an answer that isn't one of the choices.
    response = client.post(
        f"/api/quizzes/sessions/{session['id']}/answers",
        json={
            "question_id": session["question_order"][0],
            "selected_answer": "Z",
        },
    )

    assert response.status_code == 400
    assert "Invalid answer choice" in response.json()["detail"]
