from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.database import (
    AnswerChoiceRecord,
    QuestionRecord,
    QuizRecord,
)
from app.models.quiz import (
    AnswerChoice,
    Difficulty,
    Question,
    Quiz,
)
from app.services.quiz_generator import QuestionGenerator

# A session factory creates short-lived database sessions.
SessionFactory = Callable[[], Session]


class QuizService:
    """Generate and retrieve quizzes from persistent storage."""

    def __init__(
        self,
        question_generator: QuestionGenerator,
        session_factory: SessionFactory | None = None,
    ) -> None:
        self.question_generator = question_generator
        self.session_factory = session_factory

        # This fallback keeps pure unit tests independent.
        self._quizzes: dict[str, Quiz] = {}

    def _database_enabled(self) -> bool:
        """Check whether this service is using the database."""
        return self.session_factory is not None

    def generate_quiz(
        self,
        title: str,
        chunks: list[str],
        question_count: int = 5,
        source_document_id: str | None = None,
    ) -> Quiz:
        """Generate a quiz and save it permanently."""

        if not title.strip():
            raise ValueError(
                "Quiz title cannot be empty."
            )

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

        # Unit-test fallback.
        if not self._database_enabled():
            self._quizzes[quiz.id] = quiz
            return quiz

        db = self.session_factory()

        try:
            quiz_record = QuizRecord(
                id=quiz.id,
                title=quiz.title,
                description=quiz.description,
                source_document_id=quiz.source_document_id,
                created_at=datetime.now(UTC),
                is_published=False,
                updated_at=datetime.now(UTC),
            )

            # Save every question and its choices.
            for position, question in enumerate(
                quiz.questions
            ):
                question_record = QuestionRecord(
                    id=question.id,
                    quiz_id=quiz.id,
                    position=position,
                    text=question.text,
                    correct_answer=question.correct_answer,
                    explanation=question.explanation,
                    difficulty=question.difficulty.value,
                )

                question_record.choices = [
                    AnswerChoiceRecord(
                        id=choice.id,
                        question_id=question.id,
                        position=choice_position,
                        text=choice.text,
                    )
                    for choice_position, choice in enumerate(
                        question.choices
                    )
                ]

                quiz_record.questions.append(
                    question_record
                )

            db.add(quiz_record)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        return quiz

    def get_quiz(self, quiz_id: str, *, published_only: bool = False) -> Quiz:
        """Retrieve a complete quiz from the database."""

        if not self._database_enabled():
            quiz = self._quizzes.get(quiz_id)

            if quiz is None:
                raise KeyError(
                    f"Quiz '{quiz_id}' was not found."
                )

            return quiz

        db = self.session_factory()

        try:
            record = db.scalar(
                select(QuizRecord)
                .options(
                    selectinload(
                        QuizRecord.questions
                    ).selectinload(
                        QuestionRecord.choices
                    )
                )
                .where(
                    QuizRecord.id == quiz_id,
                    *([QuizRecord.is_published.is_(True)] if published_only else []),
                )
            )

            if record is None:
                raise KeyError(
                    f"Quiz '{quiz_id}' was not found."
                )

            return self._record_to_quiz(record)

        finally:
            db.close()

    def list_quizzes(self, *, published_only: bool = False) -> list[Quiz]:
        """Return stored quizzes, optionally limited to published quizzes."""

        if not self._database_enabled():
            return list(
                self._quizzes.values()
            )

        db = self.session_factory()

        try:
            query = select(QuizRecord)

            if published_only:
                query = query.where(QuizRecord.is_published.is_(True))

            records = db.scalars(
                query
                .options(
                    selectinload(
                        QuizRecord.questions
                    ).selectinload(
                        QuestionRecord.choices
                    )
                )
                .order_by(
                    QuizRecord.created_at.desc()
                )
            ).unique().all()

            return [
                self._record_to_quiz(record)
                for record in records
            ]

        finally:
            db.close()

    def update_quiz(
        self,
        quiz_id: str,
        *,
        title: str,
        description: str | None,
        is_published: bool,
    ) -> Quiz:
        """Update teacher-controlled quiz metadata and availability."""
        if not title.strip():
            raise ValueError("Quiz title cannot be empty.")

        if not self._database_enabled():
            quiz = self._quizzes.get(quiz_id)
            if quiz is None:
                raise KeyError(f"Quiz '{quiz_id}' was not found.")
            quiz.title = title.strip()
            quiz.description = description
            quiz.is_published = is_published
            return quiz

        db = self.session_factory()
        try:
            record = db.scalar(select(QuizRecord).where(QuizRecord.id == quiz_id))
            if record is None:
                raise KeyError(f"Quiz '{quiz_id}' was not found.")

            record.title = title.strip()
            record.description = description
            record.is_published = is_published
            record.updated_at = datetime.now(UTC)
            db.commit()
            db.refresh(record)
            # Re-read with relationships so the returned object is complete.
            return self.get_quiz(quiz_id)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def update_question(
        self,
        quiz_id: str,
        question_id: str,
        *,
        text: str,
        correct_answer: str,
        explanation: str | None,
        difficulty: Difficulty,
        choices: list[AnswerChoice],
    ) -> Quiz:
        """Edit one generated question and its answer choices."""
        if not text.strip() or not choices:
            raise ValueError("A question needs text and at least one choice.")
        if correct_answer not in {choice.id for choice in choices}:
            raise ValueError("The correct answer must match one of the choices.")

        if not self._database_enabled():
            raise KeyError("Question editing requires the database.")

        db = self.session_factory()
        try:
            question = db.scalar(
                select(QuestionRecord).where(
                    QuestionRecord.id == question_id,
                    QuestionRecord.quiz_id == quiz_id,
                )
            )
            if question is None:
                raise KeyError(f"Question '{question_id}' was not found.")

            question.text = text.strip()
            question.correct_answer = correct_answer
            question.explanation = explanation
            question.difficulty = difficulty.value
            question.choices.clear()
            question.choices = [
                AnswerChoiceRecord(
                    id=choice.id,
                    question_id=question_id,
                    position=index,
                    text=choice.text.strip(),
                )
                for index, choice in enumerate(choices)
            ]

            quiz = db.scalar(select(QuizRecord).where(QuizRecord.id == quiz_id))
            quiz.updated_at = datetime.now(UTC)
            db.commit()
            return self.get_quiz(quiz_id)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _record_to_quiz(
        record: QuizRecord,
    ) -> Quiz:
        """Convert a database record back into our domain model."""

        return Quiz(
            id=record.id,
            title=record.title,
            description=record.description,
            source_document_id=record.source_document_id,
            is_published=record.is_published,
            questions=[
                Question(
                    id=question.id,
                    text=question.text,
                    correct_answer=question.correct_answer,
                    explanation=question.explanation,
                    difficulty=Difficulty(
                        question.difficulty
                    ),
                    choices=[
                        AnswerChoice(
                            id=choice.id,
                            text=choice.text,
                        )
                        for choice in question.choices
                    ],
                )
                for question in record.questions
            ],
        )
