from uuid import uuid4

from app.models.quiz import Quiz
from app.services.quiz_generator import QuestionGenerator


class QuizService:
    """Application service responsible for quiz operations."""

    def __init__(
        self,
        question_generator: QuestionGenerator,
    ) -> None:
        self.question_generator = question_generator
        self._quizzes: dict[str, Quiz] = {}

    def generate_quiz(
        self,
        title: str,
        chunks: list[str],
        question_count: int = 5,
        source_document_id: str | None = None,
    ) -> Quiz:
        if not title.strip():
            raise ValueError("Quiz title cannot be empty.")

        questions = self.question_generator.generate_questions(
            chunks=chunks,
            question_count=question_count,
        )

        quiz = Quiz(
            id=str(uuid4()),
            title=title.strip(),
            questions=questions,
            source_document_id=source_document_id,
        )

        self._quizzes[quiz.id] = quiz

        return quiz

    def get_quiz(self, quiz_id: str) -> Quiz:
        quiz = self._quizzes.get(quiz_id)

        if quiz is None:
            raise KeyError(f"Quiz '{quiz_id}' was not found.")

        return quiz

    def list_quizzes(self) -> list[Quiz]:
        return list(self._quizzes.values())
