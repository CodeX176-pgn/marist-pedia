from fastapi import APIRouter, HTTPException, status

from app.config.settings import settings
from app.schemas.quiz import (
    AnswerChoiceSchema,
    QuestionSchema,
    QuizGenerationRequest,
    QuizGenerationResponse,
    QuizSchema,
)
from app.services.question_generator_factory import (
    create_question_generator,
)
from app.services.quiz_service import QuizService

router = APIRouter(
    prefix="/api/quizzes",
    tags=["Quizzes"],
)


def _create_quiz_service() -> QuizService:
    """Build a QuizService using the configured generator."""
    question_generator = create_question_generator(
        settings.question_generator,
    )

    return QuizService(
        question_generator=question_generator,
    )


quiz_service = _create_quiz_service()


def _quiz_to_schema(quiz) -> QuizSchema:
    """Convert the domain quiz model into an API schema."""
    return QuizSchema(
        id=quiz.id,
        title=quiz.title,
        source_document_id=quiz.source_document_id,
        description=quiz.description,
        questions=[
            QuestionSchema(
                id=question.id,
                text=question.text,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
                difficulty=question.difficulty,
                choices=[
                    AnswerChoiceSchema(
                        id=choice.id,
                        text=choice.text,
                    )
                    for choice in question.choices
                ],
            )
            for question in quiz.questions
        ],
    )


@router.post(
    "/generate",
    response_model=QuizGenerationResponse,
)
def generate_quiz(
    request: QuizGenerationRequest,
) -> QuizGenerationResponse:
    """Generate a quiz from processed document chunks."""

    try:
        quiz = quiz_service.generate_quiz(
            title=request.title,
            chunks=request.chunks,
            question_count=request.question_count,
            source_document_id=request.source_document_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        ) from exc

    return QuizGenerationResponse(
        quiz=_quiz_to_schema(quiz),
    )
