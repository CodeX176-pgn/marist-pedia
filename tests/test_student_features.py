from datetime import UTC, datetime
from uuid import uuid4

from app.core.database import SessionLocal
from app.main import app
from app.models.database import (
    AnswerChoiceRecord,
    QuestionRecord,
    QuizRecord,
)
from fastapi.testclient import TestClient

# Create a reusable FastAPI test client.
client = TestClient(app)


def create_database_quiz(
    *,
    title: str,
    description: str | None,
    is_published: bool,
) -> str:
    """
    Insert a small quiz directly into the test database.

    This lets the tests control whether the quiz is published.
    """

    quiz_id = str(uuid4())
    question_id = str(uuid4())

    db = SessionLocal()

    try:
        quiz = QuizRecord(
            id=quiz_id,
            title=title,
            description=description,
            source_document_id=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            is_published=is_published,
        )

        question = QuestionRecord(
            id=question_id,
            quiz_id=quiz_id,
            position=0,
            text="What is Python?",
            correct_answer="A",
            explanation="Python is a programming language.",
            difficulty="easy",
        )

        # Give the question two valid choices.
        question.choices = [
            AnswerChoiceRecord(
                id="A",
                question_id=question_id,
                position=0,
                text="A programming language",
            ),
            AnswerChoiceRecord(
                id="B",
                question_id=question_id,
                position=1,
                text="A database",
            ),
        ]

        quiz.questions.append(question)

        db.add(quiz)
        db.commit()

    finally:
        db.close()

    return quiz_id


def test_student_library_only_shows_published_quizzes():
    """Students should only see quizzes that a teacher published."""

    published_id = create_database_quiz(
        title="Published Biology",
        description="A biology practice quiz.",
        is_published=True,
    )

    create_database_quiz(
        title="Teacher Draft",
        description="This quiz is still being reviewed.",
        is_published=False,
    )

    response = client.get("/api/quizzes")

    assert response.status_code == 200

    quizzes = response.json()

    assert len(quizzes) == 1
    assert quizzes[0]["id"] == published_id
    assert quizzes[0]["title"] == "Published Biology"
    assert quizzes[0]["description"] == "A biology practice quiz."
    assert quizzes[0]["question_count"] == 1


def test_student_cannot_open_unpublished_quiz():
    """A student must not access a quiz that has not been published."""

    quiz_id = create_database_quiz(
        title="Private Draft",
        description="Not available yet.",
        is_published=False,
    )

    response = client.get(
        f"/api/quizzes/{quiz_id}"
    )

    assert response.status_code == 404


def test_student_can_open_published_quiz_without_correct_answers():
    """
    Students can open published quizzes, but the API must not reveal
    the correct answer before the student submits the quiz.
    """

    quiz_id = create_database_quiz(
        title="Student Quiz",
        description="Ready to take.",
        is_published=True,
    )

    response = client.get(
        f"/api/quizzes/{quiz_id}"
    )

    assert response.status_code == 200

    quiz = response.json()

    assert quiz["title"] == "Student Quiz"
    assert quiz["description"] == "Ready to take."
    assert len(quiz["questions"]) == 1

    question = quiz["questions"][0]

    assert "correct_answer" not in question
    assert "explanation" not in question


def test_student_cannot_start_unpublished_quiz():
    """Students cannot create attempts for unpublished quizzes."""

    quiz_id = create_database_quiz(
        title="Unpublished Quiz",
        description=None,
        is_published=False,
    )

    response = client.post(
        f"/api/quizzes/{quiz_id}/sessions",
        json={
            "quiz_id": quiz_id,
        },
    )

    assert response.status_code == 404


def test_student_can_start_published_quiz():
    """A student can create an attempt for a published quiz."""

    quiz_id = create_database_quiz(
        title="Published Quiz",
        description=None,
        is_published=True,
    )

    response = client.post(
        f"/api/quizzes/{quiz_id}/sessions",
        json={
            "quiz_id": quiz_id,
        },
    )

    assert response.status_code == 201

    session = response.json()

    assert session["quiz_id"] == quiz_id
    assert session["status"] == "active"
    assert len(session["question_order"]) == 1


def test_student_can_complete_quiz_and_receive_result():
    """
    Verify the complete student flow:

    open quiz → start session → answer → submit → receive result.
    """

    quiz_id = create_database_quiz(
        title="Complete Flow Quiz",
        description="End-to-end student test.",
        is_published=True,
    )

    # Start the quiz.
    start_response = client.post(
        f"/api/quizzes/{quiz_id}/sessions",
        json={
            "quiz_id": quiz_id,
        },
    )

    assert start_response.status_code == 201

    session = start_response.json()
    session_id = session["id"]

    question_id = session["question_order"][0]

    # Select the correct answer.
    answer_response = client.post(
        f"/api/quizzes/sessions/{session_id}/answers",
        json={
            "question_id": question_id,
            "selected_answer": "A",
        },
    )

    assert answer_response.status_code == 200

    # Submit the complete quiz.
    submit_response = client.post(
        f"/api/quizzes/sessions/{session_id}/submit"
    )

    assert submit_response.status_code == 200

    result = submit_response.json()

    assert result["session_id"] == session_id
    assert result["quiz_id"] == quiz_id
    assert result["score"] == 1
    assert result["total_questions"] == 1
    assert result["percentage"] == 100.0

    # Correct answers are allowed in the result because the quiz
    # has already been submitted.
    assert result["results"][0]["correct_answer"] == "A"
    assert result["results"][0]["is_correct"] is True
    assert (
        result["results"][0]["explanation"]
        == "Python is a programming language."
    )


def test_student_cannot_submit_same_session_twice():
    """A completed student attempt cannot be submitted again."""

    quiz_id = create_database_quiz(
        title="Single Submission Quiz",
        description=None,
        is_published=True,
    )

    start_response = client.post(
        f"/api/quizzes/{quiz_id}/sessions",
        json={
            "quiz_id": quiz_id,
        },
    )

    assert start_response.status_code == 201

    session_id = start_response.json()["id"]

    first_submit = client.post(
        f"/api/quizzes/sessions/{session_id}/submit"
    )

    assert first_submit.status_code == 200

    second_submit = client.post(
        f"/api/quizzes/sessions/{session_id}/submit"
    )

    assert second_submit.status_code == 400
    assert "already been submitted" in second_submit.json()["detail"]