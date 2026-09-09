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
    """Generate, retrieve, and manage persistent quizzes."""

    def __init__(
        self,
        question_generator: QuestionGenerator,
        session_factory: SessionFactory | None = None,
    ) -> None:
        self.question_generator = question_generator
        self.session_factory = session_factory

        # This fallback keeps pure unit tests independent from a database.
        self._quizzes: dict[str, Quiz] = {}

    def _database_enabled(self) -> bool:
        """Check whether this service is currently using the database."""
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

        # Newly generated quizzes start unpublished.
        # A teacher must review and publish them before students can see them.
        quiz = Quiz(
            id=str(uuid4()),
            title=title.strip(),
            questions=questions,
            source_document_id=source_document_id,
            is_published=False,
        )

        # Store the quiz in memory when a database is not being used.
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

            # Save every generated question and its answer choices.
            for position, question in enumerate(quiz.questions):
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

    def get_quiz(
        self,
        quiz_id: str,
        *,
        published_only: bool = False,
    ) -> Quiz:
        """
        Retrieve a complete quiz.

        When published_only=True, unpublished quizzes are deliberately
        invisible. This is used by the student-facing API.
        """

        # Handle the in-memory unit-test implementation.
        if not self._database_enabled():
            quiz = self._quizzes.get(quiz_id)

            if quiz is None:
                raise KeyError(
                    f"Quiz '{quiz_id}' was not found."
                )

            # Keep the in-memory implementation consistent with
            # the database implementation.
            if published_only and not quiz.is_published:
                raise KeyError(
                    f"Quiz '{quiz_id}' was not found."
                )

            return quiz

        db = self.session_factory()

        try:
            # Start with the requested quiz ID.
            filters = [
                QuizRecord.id == quiz_id,
            ]

            # Students may only retrieve published quizzes.
            if published_only:
                filters.append(
                    QuizRecord.is_published.is_(True)
                )

            record = db.scalar(
                select(QuizRecord)
                .options(
                    selectinload(
                        QuizRecord.questions
                    ).selectinload(
                        QuestionRecord.choices
                    )
                )
                .where(*filters)
            )

            if record is None:
                raise KeyError(
                    f"Quiz '{quiz_id}' was not found."
                )

            return self._record_to_quiz(record)

        finally:
            db.close()

    def list_quizzes(
        self,
        *,
        published_only: bool = False,
    ) -> list[Quiz]:
        """Return stored quizzes, optionally limited to published quizzes."""

        # Handle the in-memory unit-test implementation.
        if not self._database_enabled():
            quizzes = list(
                self._quizzes.values()
            )

            # Only expose published quizzes when requested.
            if published_only:
                quizzes = [
                    quiz
                    for quiz in quizzes
                    if quiz.is_published
                ]

            return quizzes

        db = self.session_factory()

        try:
            query = select(QuizRecord)

            # Students should only see quizzes that a teacher has published.
            if published_only:
                query = query.where(
                    QuizRecord.is_published.is_(True)
                )

            records = db.scalars(
                query
            ).all()

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
        description: str | None = None,
        is_published: bool = False,
    ) -> Quiz:
        """Update teacher-controlled quiz metadata and publication status."""

        if not title.strip():
            raise ValueError("Quiz title cannot be empty.")

        # Keep the lightweight in-memory implementation usable in unit tests.
        if not self._database_enabled():
            quiz = self._quizzes.get(quiz_id)

            if quiz is None:
                raise KeyError(
                    f"Quiz '{quiz_id}' was not found."
                )

            quiz.title = title.strip()
            quiz.description = description
            quiz.is_published = is_published
            return quiz

        db = self.session_factory()

        try:
            # Load the quiz so the teacher can update its stored metadata.
            record = db.scalar(
                select(QuizRecord)
                .options(
                    selectinload(
                        QuizRecord.questions
                    ).selectinload(
                        QuestionRecord.choices
                    )
                )
                .where(QuizRecord.id == quiz_id)
            )

            if record is None:
                raise KeyError(
                    f"Quiz '{quiz_id}' was not found."
                )

            record.title = title.strip()
            record.description = description
            record.is_published = is_published
            record.updated_at = datetime.now(UTC)

            db.commit()

            return self._record_to_quiz(record)

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
        """Update one question and its answer choices."""

        if not text.strip():
            raise ValueError("Question text cannot be empty.")

        if not choices:
            raise ValueError("A question must have at least two choices.")

        if len(choices) < 2:
            raise ValueError("A question must have at least two choices.")

        # Answer IDs must be unique within the question.
        choice_ids = [choice.id for choice in choices]
        if len(choice_ids) != len(set(choice_ids)):
            raise ValueError("Answer choice IDs must be unique.")

        # The correct answer must refer to one of the available choices.
        if correct_answer not in choice_ids:
            raise ValueError(
                "Correct answer must match one of the answer choice IDs."
            )

        # Keep the lightweight in-memory implementation usable in unit tests.
        if not self._database_enabled():
            quiz = self._quizzes.get(quiz_id)

            if quiz is None:
                raise KeyError(
                    f"Quiz '{quiz_id}' was not found."
                )

            question = next(
                (
                    item
                    for item in quiz.questions
                    if item.id == question_id
                ),
                None,
            )

            if question is None:
                raise KeyError(
                    f"Question '{question_id}' was not found."
                )

            question.text = text.strip()
            question.correct_answer = correct_answer
            question.explanation = explanation
            question.difficulty = difficulty
            question.choices = list(choices)

            return quiz

        db = self.session_factory()

        try:
            # Load the question through its quiz so the relationship is verified.
            question = db.scalar(
                select(QuestionRecord)
                .options(
                    selectinload(
                        QuestionRecord.choices
                    )
                )
                .where(
                    QuestionRecord.id == question_id,
                    QuestionRecord.quiz_id == quiz_id,
                )
            )

            if question is None:
                raise KeyError(
                    f"Question '{question_id}' was not found."
                )

            question.text = text.strip()
            question.correct_answer = correct_answer
            question.explanation = explanation
            question.difficulty = difficulty.value

            # Replacing the relationship safely removes old choices because
            # the SQLAlchemy model uses delete-orphan cascade.
            question.choices = [
                AnswerChoiceRecord(
                    id=choice.id,
                    question_id=question_id,
                    position=position,
                    text=choice.text,
                )
                for position, choice in enumerate(choices)
            ]

            quiz = db.scalar(
                select(QuizRecord)
                .options(
                    selectinload(
                        QuizRecord.questions
                    ).selectinload(
                        QuestionRecord.choices
                    )
                )
                .where(QuizRecord.id == quiz_id)
            )

            if quiz is None:
                raise KeyError(
                    f"Quiz '{quiz_id}' was not found."
                )

            quiz.updated_at = datetime.now(UTC)

            db.commit()

            # Reload the committed relationship state before returning it.
            db.refresh(quiz)

            return self._record_to_quiz(quiz)

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    @staticmethod
    def _record_to_quiz(
        record: QuizRecord,
    ) -> Quiz:
        """Convert a database record into the application's Quiz model."""

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