from app.models.quiz import (
    AnswerChoice,
    Difficulty,
    Question,
    Quiz,
    QuizSessionStatus,
)
from app.services.quiz_session_service import (
    QuizSessionService,
)


def create_test_quiz() -> Quiz:
    return Quiz(
        id="quiz-1",
        title="Test Quiz",
        questions=[
            Question(
                id="q1",
                text="What is Python?",
                choices=[
                    AnswerChoice(
                        id="A",
                        text="A programming language",
                    ),
                    AnswerChoice(
                        id="B",
                        text="A database",
                    ),
                ],
                correct_answer="A",
                explanation="Python is a programming language.",
                difficulty=Difficulty.EASY,
            ),
            Question(
                id="q2",
                text="What is FastAPI?",
                choices=[
                    AnswerChoice(
                        id="A",
                        text="A game engine",
                    ),
                    AnswerChoice(
                        id="B",
                        text="A Python web framework",
                    ),
                ],
                correct_answer="B",
                explanation="FastAPI is a Python web framework.",
                difficulty=Difficulty.MEDIUM,
            ),
        ],
    )


def test_create_session():
    service = QuizSessionService()
    quiz = create_test_quiz()

    session = service.create_session(quiz)

    assert session.id
    assert session.quiz_id == "quiz-1"
    assert session.question_order == ["q1", "q2"]
    assert session.answers == {}
    assert session.status == QuizSessionStatus.ACTIVE


def test_submit_answer():
    service = QuizSessionService()
    quiz = create_test_quiz()

    session = service.create_session(quiz)

    service.submit_answer(
        session_id=session.id,
        quiz=quiz,
        question_id="q1",
        selected_answer="A",
    )

    stored_session = service.get_session(session.id)

    assert stored_session.answers["q1"] == "A"


def test_submit_quiz_calculates_score():
    service = QuizSessionService()
    quiz = create_test_quiz()

    session = service.create_session(quiz)

    service.submit_answer(
        session_id=session.id,
        quiz=quiz,
        question_id="q1",
        selected_answer="A",
    )

    service.submit_answer(
        session_id=session.id,
        quiz=quiz,
        question_id="q2",
        selected_answer="A",
    )

    result = service.submit_session(
        session_id=session.id,
        quiz=quiz,
    )

    assert result["score"] == 1
    assert result["total_questions"] == 2
    assert result["percentage"] == 50.0

    assert result["results"][0]["is_correct"] is True
    assert result["results"][1]["is_correct"] is False


def test_submitted_session_cannot_be_submitted_again():
    service = QuizSessionService()
    quiz = create_test_quiz()

    session = service.create_session(quiz)

    service.submit_session(
        session_id=session.id,
        quiz=quiz,
    )

    try:
        service.submit_session(
            session_id=session.id,
            quiz=quiz,
        )
    except ValueError as exc:
        assert "already been submitted" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )