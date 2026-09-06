from pydantic import BaseModel, Field


class QuizCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    document_id: str | None = None
    question_count: int = Field(default=5, ge=1, le=50)


class QuestionResponse(BaseModel):
    id: str
    question: str
    options: list[str]
    explanation: str | None = None


class QuizResponse(BaseModel):
    id: str
    title: str
    document_id: str | None = None
    questions: list[QuestionResponse]
