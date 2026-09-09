from fastapi import APIRouter, HTTPException, status

from app.config.settings import settings
from app.core.database import SessionLocal
from app.schemas.quiz import (
    AnswerChoiceSchema,
    AnswerSubmission,
    AnswerSubmissionResponse,
    QuestionSchema,
    QuizGenerationRequest,
    QuizGenerationResponse,
    QuizResultResponse,
    QuizSchema,
    QuizSessionCreateRequest,
    QuizSessionResponse,
    QuizSummarySchema,
)
from app.services.question_generator_factory import (
    create_question_generator,
)
from app.services.quiz_service import QuizService
from app.services.quiz_session_service import (
    QuizSessionService,
)

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
        session_factory=SessionLocal,
    )


quiz_service = _create_quiz_service()
session_service = QuizSessionService(
    session_factory=SessionLocal,
)

def _question_to_schema(question) -> QuestionSchema:
    return QuestionSchema(
        id=question.id,
        text=question.text,
        difficulty=question.difficulty,
        choices=[
            AnswerChoiceSchema(
                id=choice.id,
                text=choice.text,
            )
            for choice in question.choices
        ],
    )


def _quiz_to_schema(quiz) -> QuizSchema:
    return QuizSchema(
        id=quiz.id,
        title=quiz.title,
        source_document_id=quiz.source_document_id,
        description=quiz.description,
        questions=[
            _question_to_schema(question)
            for question in quiz.questions
        ],
    )


def _session_to_schema(session) -> QuizSessionResponse:
    return QuizSessionResponse(
        id=session.id,
        quiz_id=session.quiz_id,
        question_order=session.question_order,
        status=session.status,
        started_at=session.started_at,
    )


@router.post(
    "/generate",
    response_model=QuizGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_quiz(
    request: QuizGenerationRequest,
) -> QuizGenerationResponse:
    """Generate and store a quiz."""

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


@router.get(
    "",
    response_model=list[QuizSummarySchema],
)
def list_quizzes() -> list[QuizSummarySchema]:
    """Return all available quizzes."""

    return [
        QuizSummarySchema(
            id=quiz.id,
            title=quiz.title,
            question_count=len(quiz.questions),
            source_document_id=quiz.source_document_id,
        )
        for quiz in quiz_service.list_quizzes(published_only=True)
    ]


@router.get(
    "/{quiz_id}",
    response_model=QuizSchema,
)
def get_quiz(quiz_id: str) -> QuizSchema:
    """Return a quiz without exposing its correct answers."""

    try:
        quiz = quiz_service.get_quiz(quiz_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return _quiz_to_schema(quiz)


@router.post(
    "/{quiz_id}/sessions",
    response_model=QuizSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    quiz_id: str,
    request: QuizSessionCreateRequest,
) -> QuizSessionResponse:
    """Create a new attempt for a quiz."""

    if request.quiz_id != quiz_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz ID in request does not match URL.",
        )

    try:
        quiz = quiz_service.get_quiz(quiz_id)
        session = session_service.create_session(quiz)

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return _session_to_schema(session)


@router.get(
    "/sessions/{session_id}",
    response_model=QuizSessionResponse,
)
def get_session(session_id: str) -> QuizSessionResponse:
    """Return the current state of a quiz session."""

    try:
        session = session_service.get_session(session_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return _session_to_schema(session)


@router.post(
    "/sessions/{session_id}/answers",
    response_model=AnswerSubmissionResponse,
)
def submit_answer(
    session_id: str,
    request: AnswerSubmission,
) -> AnswerSubmissionResponse:
    """Record one answer in an active quiz session."""

    try:
        session = session_service.get_session(session_id)
        quiz = quiz_service.get_quiz(session.quiz_id)

        session_service.submit_answer(
            session_id=session_id,
            quiz=quiz,
            question_id=request.question_id,
            selected_answer=request.selected_answer,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return AnswerSubmissionResponse(
        session_id=session_id,
        question_id=request.question_id,
        selected_answer=request.selected_answer,
    )


@router.post(
    "/sessions/{session_id}/submit",
    response_model=QuizResultResponse,
)
def submit_session(
    session_id: str,
) -> QuizResultResponse:
    """Submit and evaluate an entire quiz session."""

    try:
        session = session_service.get_session(session_id)
        quiz = quiz_service.get_quiz(session.quiz_id)

        result = session_service.submit_session(
            session_id=session_id,
            quiz=quiz,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return QuizResultResponse(**result)