from datetime import datetime

from pydantic import BaseModel, Field

from app.models.quiz import Difficulty, QuizSessionStatus


class AnswerChoiceSchema(BaseModel):
    id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class QuestionSchema(BaseModel):
    id: str
    text: str = Field(min_length=1)
    choices: list[AnswerChoiceSchema] = Field(min_length=2)
    difficulty: Difficulty


class QuestionWithAnswerSchema(QuestionSchema):
    correct_answer: str
    explanation: str | None = None


class QuizSchema(BaseModel):
    id: str
    title: str = Field(min_length=1)
    questions: list[QuestionSchema]
    source_document_id: str | None = None
    description: str | None = None


class QuizGenerationRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    chunks: list[str] = Field(min_length=1)
    question_count: int = Field(default=5, ge=1, le=50)
    source_document_id: str | None = None


class QuizGenerationResponse(BaseModel):
    quiz: QuizSchema


class QuizSummarySchema(BaseModel):
    id: str
    title: str
    question_count: int
    source_document_id: str | None = None


class QuizSessionCreateRequest(BaseModel):
    quiz_id: str


class QuizSessionResponse(BaseModel):
    id: str
    quiz_id: str
    question_order: list[str]
    status: QuizSessionStatus
    started_at: datetime


class AnswerSubmission(BaseModel):
    question_id: str
    selected_answer: str = Field(min_length=1)


class AnswerSubmissionResponse(BaseModel):
    session_id: str
    question_id: str
    selected_answer: str


class QuizResultItem(BaseModel):
    question_id: str
    selected_answer: str | None
    correct_answer: str
    is_correct: bool
    explanation: str | None = None


class QuizResultResponse(BaseModel):
    session_id: str
    quiz_id: str
    score: int
    total_questions: int
    percentage: float
    results: list[QuizResultItem]
    submitted_at: datetime