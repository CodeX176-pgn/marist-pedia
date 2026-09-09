from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.admin_auth import require_admin
from app.core.database import SessionLocal
from app.models.database import DocumentRecord, QuizRecord
from app.models.quiz import AnswerChoice
from app.schemas.admin import (
    AdminDocumentSchema,
    AdminQuizSchema,
    AdminQuizSummarySchema,
    QuestionUpdateRequest,
    QuizUpdateRequest,
)
from app.services.document_service import delete_document
from app.services.quiz_service import QuizService
from app.config.settings import settings
from app.services.question_generator_factory import create_question_generator

router = APIRouter(
    prefix="/api/admin",
    tags=["Teacher/Admin"],
    dependencies=[Depends(require_admin)],
)


def _quiz_service() -> QuizService:
    """Build the normal quiz service for teacher operations."""
    return QuizService(
        question_generator=create_question_generator(settings.question_generator),
        session_factory=SessionLocal,
    )


@router.get("/documents", response_model=list[AdminDocumentSchema])
def list_documents() -> list[AdminDocumentSchema]:
    """List uploaded documents for the teacher dashboard."""
    db = SessionLocal()
    try:
        records = db.scalars(
            select(DocumentRecord).order_by(DocumentRecord.uploaded_at.desc())
        ).all()
        return [AdminDocumentSchema.model_validate(record, from_attributes=True) for record in records]
    finally:
        db.close()


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(document_id: str) -> None:
    """Delete a document from storage and the database."""
    try:
        delete_document(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/quizzes", response_model=list[AdminQuizSummarySchema])
def list_all_quizzes() -> list[AdminQuizSummarySchema]:
    """List published and unpublished quizzes for teacher review."""
    db = SessionLocal()
    try:
        records = db.scalars(
            select(QuizRecord)
            .options(selectinload(QuizRecord.questions))
            .order_by(QuizRecord.created_at.desc())
        ).unique().all()
        return [
            AdminQuizSummarySchema(
                id=record.id,
                title=record.title,
                description=record.description,
                question_count=len(record.questions),
                source_document_id=record.source_document_id,
                is_published=record.is_published,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            for record in records
        ]
    finally:
        db.close()


@router.get("/quizzes/{quiz_id}", response_model=AdminQuizSchema)
def get_admin_quiz(quiz_id: str):
    """Return the full quiz, including answers, for teacher review."""
    try:
        quiz = _quiz_service().get_quiz(quiz_id)
        return {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "source_document_id": quiz.source_document_id,
            "is_published": quiz.is_published,
            "questions": [
                {
                    "id": question.id,
                    "text": question.text,
                    "choices": [choice.__dict__ for choice in question.choices],
                    "correct_answer": question.correct_answer,
                    "explanation": question.explanation,
                    "difficulty": question.difficulty,
                }
                for question in quiz.questions
            ],
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/quizzes/{quiz_id}")
def update_quiz(quiz_id: str, request: QuizUpdateRequest):
    """Update title, description, and publication status."""
    try:
        return _quiz_service().update_quiz(
            quiz_id,
            title=request.title,
            description=request.description,
            is_published=request.is_published,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/quizzes/{quiz_id}/questions/{question_id}")
def update_question(
    quiz_id: str,
    question_id: str,
    request: QuestionUpdateRequest,
):
    """Update one question while preserving its quiz relationship."""
    try:
        quiz = _quiz_service().update_question(
            quiz_id,
            question_id,
            text=request.text,
            correct_answer=request.correct_answer,
            explanation=request.explanation,
            difficulty=request.difficulty,
            choices=[AnswerChoice(id=choice.id, text=choice.text) for choice in request.choices],
        )
        return quiz
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
