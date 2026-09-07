
from fastapi import APIRouter, HTTPException

from app.schemas.quiz import (
    AnswerChoiceSchema,
    QuestionSchema,
    QuizGenerationRequest,
    QuizGenerationResponse,
    QuizSchema,
)
from app.services.quiz_service import QuizService

router = APIRouter(
    prefix="/api/quizzes",
    tags=["quizzes"],
)

quiz_service = QuizService()


@router.post(
    "/generate",
    response_model=QuizGenerationResponse,
)
def generate_quiz(
    request: QuizGenerationRequest,
) -> QuizGenerationResponse:
    """Generate a quiz from processed text chunks."""

    try:
        quiz = quiz_service.generate_quiz(
            title=request.title,
            chunks=request.chunks,
            question_count=request.question_count,
            source_document_id=request.source_document_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    quiz_schema = QuizSchema(
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

    return QuizGenerationResponse(
        quiz=quiz_schema,
    )
