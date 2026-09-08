from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.database import (
    QuizAnswerRecord,
    QuizResultItemRecord,
    QuizResultRecord,
    QuizSessionRecord,
)
from app.models.quiz import (
    Quiz,
    QuizSession,
    QuizSessionStatus,
)

SessionFactory = Callable[[], Session]


class QuizSessionService:
    """Manage persistent quiz sessions and evaluation."""

    def __init__(
        self,
        session_factory: SessionFactory | None = None,
    ) -> None:
        self.session_factory = session_factory

        # Used only when running isolated unit tests.
        self._sessions: dict[str, QuizSession] = {}

    def create_session(
        self,
        quiz: Quiz,
    ) -> QuizSession:
        """Create and persist a new quiz session."""

        if not quiz.questions:
            raise ValueError(
                "Cannot create a session for a quiz with no questions."
            )

        session = QuizSession(
            id=str(uuid4()),
            quiz_id=quiz.id,
            question_order=[
                question.id
                for question in quiz.questions
            ],
        )

        if self.session_factory is None:
            self._sessions[session.id] = session
            return session

        db = self.session_factory()

        try:
            record = QuizSessionRecord(
                id=session.id,
                quiz_id=session.quiz_id,
                status=session.status.value,
                question_order=session.question_order,
                started_at=session.started_at,
            )

            db.add(record)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        return session

    def get_session(
        self,
        session_id: str,
    ) -> QuizSession:
        """Retrieve a session from persistent storage."""

        if self.session_factory is None:
            session = self._sessions.get(
                session_id
            )

            if session is None:
                raise KeyError(
                    f"Quiz session '{session_id}' was not found."
                )

            return session

        db = self.session_factory()

        try:
            record = db.scalar(
                select(QuizSessionRecord)
                .options(
                    selectinload(
                        QuizSessionRecord.answers
                    )
                )
                .where(
                    QuizSessionRecord.id
                    == session_id
                )
            )

            if record is None:
                raise KeyError(
                    f"Quiz session '{session_id}' was not found."
                )

            return self._record_to_session(record)

        finally:
            db.close()

    def submit_answer(
        self,
        session_id: str,
        quiz: Quiz,
        question_id: str,
        selected_answer: str,
    ) -> QuizSession:
        """Save one answer for a quiz session."""

        session = self.get_session(
            session_id
        )

        if session.status != QuizSessionStatus.ACTIVE:
            raise ValueError(
                "This quiz session has already been submitted."
            )

        question = next(
            (
                question
                for question in quiz.questions
                if question.id == question_id
            ),
            None,
        )

        if question is None:
            raise KeyError(
                f"Question '{question_id}' was not found."
            )

        valid_choice_ids = {
            choice.id
            for choice in question.choices
        }

        if selected_answer not in valid_choice_ids:
            raise ValueError(
                f"Invalid answer choice '{selected_answer}'."
            )

        if question_id not in session.question_order:
            raise ValueError(
                "Question does not belong to this quiz session."
            )

        if self.session_factory is None:
            session.answers[question_id] = (
                selected_answer
            )
            return session

        db = self.session_factory()

        try:
            answer = db.get(
                QuizAnswerRecord,
                (session_id, question_id),
            )

            if answer is None:
                answer = QuizAnswerRecord(
                    session_id=session_id,
                    question_id=question_id,
                    selected_answer=selected_answer,
                )

                db.add(answer)

            else:
                answer.selected_answer = (
                    selected_answer
                )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        session.answers[question_id] = (
            selected_answer
        )

        return session

    def submit_session(
        self,
        session_id: str,
        quiz: Quiz,
    ) -> dict:
        """Evaluate a session and permanently save its result."""

        session = self.get_session(
            session_id
        )

        if session.status != QuizSessionStatus.ACTIVE:
            raise ValueError(
                "This quiz session has already been submitted."
            )

        results = []
        score = 0

        for question in quiz.questions:
            selected_answer = session.answers.get(
                question.id
            )

            is_correct = (
                selected_answer
                == question.correct_answer
            )

            if is_correct:
                score += 1

            results.append(
                {
                    "question_id": question.id,
                    "selected_answer": selected_answer,
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                    "explanation": question.explanation,
                }
            )

        submitted_at = datetime.now(UTC)
        total_questions = len(
            quiz.questions
        )

        percentage = (
            (score / total_questions) * 100
            if total_questions
            else 0.0
        )

        if self.session_factory is None:
            session.status = (
                QuizSessionStatus.SUBMITTED
            )
            session.completed_at = submitted_at

        else:
            db = self.session_factory()

            try:
                record = db.get(
                    QuizSessionRecord,
                    session_id,
                )

                if record is None:
                    raise KeyError(
                        f"Quiz session '{session_id}' was not found."
                    )

                record.status = (
                    QuizSessionStatus.SUBMITTED.value
                )
                record.completed_at = (
                    submitted_at
                )

                result_record = QuizResultRecord(
                    session_id=session_id,
                    score=score,
                    total_questions=total_questions,
                    percentage=round(
                        percentage,
                        2,
                    ),
                    submitted_at=submitted_at,
                )

                result_record.items = [
                    QuizResultItemRecord(
                        session_id=session_id,
                        question_id=item[
                            "question_id"
                        ],
                        position=position,
                        selected_answer=item[
                            "selected_answer"
                        ],
                        correct_answer=item[
                            "correct_answer"
                        ],
                        is_correct=item[
                            "is_correct"
                        ],
                        explanation=item[
                            "explanation"
                        ],
                    )
                    for position, item in enumerate(
                        results
                    )
                ]

                db.add(result_record)
                db.commit()

            except Exception:
                db.rollback()
                raise

            finally:
                db.close()

            session.status = (
                QuizSessionStatus.SUBMITTED
            )
            session.completed_at = submitted_at

        return {
            "session_id": session.id,
            "quiz_id": quiz.id,
            "score": score,
            "total_questions": total_questions,
            "percentage": round(
                percentage,
                2,
            ),
            "results": results,
            "submitted_at": submitted_at,
        }

    @staticmethod
    def _record_to_session(
        record: QuizSessionRecord,
    ) -> QuizSession:
        """Convert a database session to the domain model."""

        return QuizSession(
            id=record.id,
            quiz_id=record.quiz_id,
            question_order=list(
                record.question_order
            ),
            answers={
                answer.question_id:
                    answer.selected_answer
                for answer in record.answers
            },
            status=QuizSessionStatus(
                record.status
            ),
            started_at=record.started_at,
            completed_at=record.completed_at,
        )
