from app.services.ai_question_generator import AIQuestionGenerator
from app.services.local_question_generator import LocalQuestionGenerator
from app.services.quiz_generator import QuestionGenerator


def create_question_generator(
    generator_type: str,
) -> QuestionGenerator:
    """Create the configured question-generator implementation."""

    normalized_type = generator_type.strip().lower()

    if normalized_type == "local":
        return LocalQuestionGenerator()

    if normalized_type == "ai":
        return AIQuestionGenerator()

    raise ValueError(
        f"Unsupported question generator: {generator_type}"
    )
