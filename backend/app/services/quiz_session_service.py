from datetime import UTC, datetime
from uuid import uuid4

from app.models.quiz import (
    Quiz,
    QuizSession,
    QuizSessionStatus,
)


class QuizSessionService:
    """Manage active quiz sessions and evaluate submissions."""

    def __init__(self) -> None:
        self._sessions: dict[str, QuizSession] = {}

    def create_session(self, quiz: Quiz) -> QuizSession:
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

        self._sessions[session.id] = session

        return session

    def get_session(self, session_id: str) -> QuizSession:
        session = self._sessions.get(session_id)

        if session is None:
            raise KeyError(
                f"Quiz session '{session_id}' was not found."
            )

        return session

    def submit_answer(
        self,
        session_id: str,
        quiz: Quiz,
        question_id: str,
        selected_answer: str,
    ) -> QuizSession:
        session = self.get_session(session_id)

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

        session.answers[question_id] = selected_answer

        return session

    def submit_session(
        self,
        session_id: str,
        quiz: Quiz,
    ) -> dict:
        session = self.get_session(session_id)

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
                selected_answer == question.correct_answer
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

        session.status = QuizSessionStatus.SUBMITTED
        session.completed_at = datetime.now(UTC)

        total_questions = len(quiz.questions)

        percentage = (
            (score / total_questions) * 100
            if total_questions
            else 0.0
        )

        return {
            "session_id": session.id,
            "quiz_id": quiz.id,
            "score": score,
            "total_questions": total_questions,
            "percentage": round(percentage, 2),
            "results": results,
            "submitted_at": session.completed_at,
        }