from pydantic import BaseModel, Field

from app.models.quiz import Difficulty


class AnswerChoiceSchema(BaseModel):
    id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class QuestionSchema(BaseModel):
    id: str
    text: str = Field(min_length=1)
    choices: list[AnswerChoiceSchema] = Field(min_length=2)
    correct_answer: str
    explanation: str | None = None
    difficulty: Difficulty


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
