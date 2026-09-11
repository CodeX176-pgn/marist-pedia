from app.models.quiz import Question
from app.services.quiz_generator import QuestionGenerator


class AIQuestionGenerator(QuestionGenerator):
    """Generate questions through a future AI provider integration."""

    def generate_questions(
        self,
        chunks: list[str],
        question_count: int,
    ) -> list[Question]:
        raise NotImplementedError(
            "AI question generation is not configured yet."
        )
