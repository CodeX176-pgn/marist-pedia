from datetime import datetime

from pydantic import BaseModel, Field

from app.models.quiz import Difficulty


class AdminDocumentSchema(BaseModel):
    id: str
    original_filename: str
    extension: str
    size: int
    uploaded_at: datetime


class AdminQuizSummarySchema(BaseModel):
    id: str
    title: str
    description: str | None = None
    question_count: int
    source_document_id: str | None = None
    is_published: bool
    created_at: datetime
    updated_at: datetime


class QuizUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    is_published: bool = False


class AdminAnswerChoice(BaseModel):
    id: str = Field(min_length=1, max_length=20)
    text: str = Field(min_length=1, max_length=2000)


class QuestionUpdateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    choices: list[AdminAnswerChoice] = Field(min_length=2, max_length=10)
    correct_answer: str = Field(min_length=1, max_length=20)
    explanation: str | None = Field(default=None, max_length=5000)
    difficulty: Difficulty = Difficulty.MEDIUM


class AdminQuestionSchema(BaseModel):
    id: str
    text: str
    choices: list[AdminAnswerChoice]
    correct_answer: str
    explanation: str | None = None
    difficulty: Difficulty


class AdminQuizSchema(BaseModel):
    id: str
    title: str
    description: str | None = None
    source_document_id: str | None = None
    is_published: bool
    questions: list[AdminQuestionSchema]
