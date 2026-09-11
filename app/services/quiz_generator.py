from abc import ABC, abstractmethod

from app.models.quiz import Question


class QuestionGenerator(ABC):
    """Contract for components that generate quiz questions."""

    @abstractmethod
    def generate_questions(
        self,
        chunks: list[str],
        question_count: int,
    ) -> list[Question]:
        """Generate questions from processed document chunks."""
        raise NotImplementedError
