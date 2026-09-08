from app.core.database import SessionLocal
from app.models.database import QuizResultRecord
from app.services.local_question_generator import (
    LocalQuestionGenerator,
)
from app.services.quiz_service import QuizService
from app.services.quiz_session_service import (
    QuizSessionService,
)


def test_quiz_persists_across_service_instances() -> None:
    """A new service can retrieve an existing database quiz."""

    first_service = QuizService(
        question_generator=LocalQuestionGenerator(),
        session_factory=SessionLocal,
    )

    second_service = QuizService(
        question_generator=LocalQuestionGenerator(),
        session_factory=SessionLocal,
    )

    quiz = first_service.generate_quiz(
        title="Persistent Quiz",
        chunks=[
            "Python is a programming language."
        ],
        question_count=1,
    )

    stored_quiz = second_service.get_quiz(
        quiz.id
    )

    assert stored_quiz.id == quiz.id
    assert stored_quiz.title == "Persistent Quiz"
    assert len(stored_quiz.questions) == 1


def test_quiz_result_persists() -> None:
    """Submitted results are saved in SQLite."""

    quiz_service = QuizService(
        question_generator=LocalQuestionGenerator(),
        session_factory=SessionLocal,
    )

    session_service = QuizSessionService(
        session_factory=SessionLocal,
    )

    quiz = quiz_service.generate_quiz(
        title="Result Quiz",
        chunks=[
            "Python is a programming language."
        ],
        question_count=1,
    )

    session = session_service.create_session(
        quiz
    )

    session_service.submit_answer(
        session_id=session.id,
        quiz=quiz,
        question_id=quiz.questions[0].id,
        selected_answer="A",
    )

    result = session_service.submit_session(
        session.id,
        quiz,
    )

    # Open a completely new database session.
    with SessionLocal() as db:
        stored_result = db.get(
            QuizResultRecord,
            session.id,
        )

    assert stored_result is not None
    assert stored_result.score == result["score"]
    assert stored_result.total_questions == 1
