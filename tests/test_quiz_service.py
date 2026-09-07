from app.models.quiz import Difficulty
from app.services.local_question_generator import LocalQuestionGenerator
from app.services.quiz_service import QuizService


def test_generate_quiz():
    service = QuizService(
        question_generator=LocalQuestionGenerator(),
    )

    chunks = [
        (
            "Python is a high-level programming language designed "
            "for general-purpose programming."
        ),
        "FastAPI is a modern Python web framework for building APIs.",
    ]

    quiz = service.generate_quiz(
        title="Python Quiz",
        chunks=chunks,
        question_count=2,
    )

    assert quiz.title == "Python Quiz"
    assert len(quiz.questions) == 2

    for question in quiz.questions:
        assert question.id
        assert question.text
        assert len(question.choices) == 4
        assert question.correct_answer == "A"
        assert question.explanation
        assert question.difficulty == Difficulty.MEDIUM


def test_generate_quiz_requires_chunks():
    service = QuizService(
        question_generator=LocalQuestionGenerator(),
    )

    try:
        service.generate_quiz(
            title="Empty Quiz",
            chunks=[],
            question_count=5,
        )
    except ValueError as exc:
        assert str(exc) == "At least one text chunk is required."
    else:
        raise AssertionError("Expected ValueError")


def test_generate_quiz_requires_positive_question_count():
    service = QuizService(
        question_generator=LocalQuestionGenerator(),
    )

    try:
        service.generate_quiz(
            title="Invalid Quiz",
            chunks=["This is valid source content for a quiz."],
            question_count=0,
        )
    except ValueError as exc:
        assert str(exc) == "Question count must be at least 1."
    else:
        raise AssertionError("Expected ValueError")


def test_question_count_cannot_exceed_available_sentences():
    service = QuizService(
        question_generator=LocalQuestionGenerator(),
    )

    chunks = [
        "Python is a programming language.",
        "FastAPI is a web framework.",
    ]

    quiz = service.generate_quiz(
        title="Technology Quiz",
        chunks=chunks,
        question_count=10,
    )

    assert len(quiz.questions) == 2
