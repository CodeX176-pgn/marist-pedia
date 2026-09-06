from fastapi import APIRouter, status

from app.schemas.quiz import QuizCreate, QuizResponse
from app.services.quiz_service import create_quiz

router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"],
)


@router.post(
    "",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_quiz_endpoint(payload: QuizCreate) -> QuizResponse:
    quiz = create_quiz(
        title=payload.title,
        document_id=payload.document_id,
        question_count=payload.question_count,
    )

    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        document_id=quiz.document_id,
        questions=[],
    )
