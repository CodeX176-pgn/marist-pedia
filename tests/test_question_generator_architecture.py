from app.models.quiz import Question
from app.services.ai_question_generator import AIQuestionGenerator
from app.services.local_question_generator import LocalQuestionGenerator
from app.services.question_generator_factory import (
    create_question_generator,
)
from app.services.quiz_generator import QuestionGenerator
from app.services.quiz_service import QuizService


def test_local_generator_implements_question_generator():
    generator = LocalQuestionGenerator()

    assert isinstance(generator, QuestionGenerator)


def test_ai_generator_implements_question_generator():
    generator = AIQuestionGenerator()

    assert isinstance(generator, QuestionGenerator)


def test_factory_creates_local_generator():
    generator = create_question_generator("local")

    assert isinstance(generator, LocalQuestionGenerator)


def test_factory_creates_ai_generator():
    generator = create_question_generator("ai")

    assert isinstance(generator, AIQuestionGenerator)


def test_factory_rejects_unknown_generator():
    try:
        create_question_generator("unknown")
    except ValueError as exc:
        assert "Unsupported question generator" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_quiz_service_accepts_custom_generator():
    class FakeQuestionGenerator(QuestionGenerator):
        def generate_questions(
            self,
            chunks: list[str],
            question_count: int,
        ) -> list[Question]:
            return []

    service = QuizService(
        question_generator=FakeQuestionGenerator(),
    )

    quiz = service.generate_quiz(
        title="Test Quiz",
        chunks=["This chunk is intentionally unused."],
    )

    assert quiz.questions == []
