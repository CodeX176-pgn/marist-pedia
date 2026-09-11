from datetime import datetime

from pydantic import BaseModel, Field

from app.models.quiz import Difficulty, QuizSessionStatus


class AnswerChoiceSchema(BaseModel):
    """Describe one answer choice without revealing whether it is correct."""

    id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class QuestionSchema(BaseModel):
    """Describe a question that is safe to send before submission."""

    id: str
    text: str = Field(min_length=1)
    choices: list[AnswerChoiceSchema] = Field(min_length=2)
    difficulty: Difficulty


class QuestionWithAnswerSchema(QuestionSchema):
    """Describe a question after a quiz has been submitted."""

    correct_answer: str
    explanation: str | None = None


class QuizSchema(BaseModel):
    """Describe a complete student-accessible quiz."""

    id: str
    title: str = Field(min_length=1)
    questions: list[QuestionSchema]
    source_document_id: str | None = None
    description: str | None = None


class QuizGenerationRequest(BaseModel):
    """Data required when a teacher/system generates a new quiz."""

    title: str = Field(min_length=1, max_length=200)
    chunks: list[str] = Field(min_length=1)
    question_count: int = Field(default=5, ge=1, le=50)
    source_document_id: str | None = None


class QuizGenerationResponse(BaseModel):
    """Return the newly generated quiz."""

    quiz: QuizSchema


class QuizSummarySchema(BaseModel):
    """Small amount of quiz information shown in the student library."""

    id: str
    title: str
    description: str | None = None
    question_count: int
    source_document_id: str | None = None


class QuizSessionCreateRequest(BaseModel):
    """Identify the quiz for which a student wants to start an attempt."""

    quiz_id: str


class QuizSessionResponse(BaseModel):
    """Represent the student's active or completed quiz session."""

    id: str
    quiz_id: str
    question_order: list[str]
    status: QuizSessionStatus
    started_at: datetime


class AnswerSubmission(BaseModel):
    """Represent one answer selected by a student."""

    question_id: str
    selected_answer: str = Field(min_length=1)


class AnswerSubmissionResponse(BaseModel):
    """Confirm that an answer was accepted by the server."""

    session_id: str
    question_id: str
    selected_answer: str


class QuizResultItem(BaseModel):
    """Represent the result for one question after submission."""

    question_id: str
    selected_answer: str | None
    correct_answer: str
    is_correct: bool
    explanation: str | None = None


class QuizResultResponse(BaseModel):
    """Return the complete result after a student submits a quiz."""

    session_id: str
    quiz_id: str
    score: int
    total_questions: int
    percentage: float
    results: list[QuizResultItem]
    submitted_at: datetime