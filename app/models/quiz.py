from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizSessionStatus(StrEnum):
    ACTIVE = "active"
    SUBMITTED = "submitted"


@dataclass
class AnswerChoice:
    id: str
    text: str


@dataclass
class Question:
    id: str
    text: str
    choices: list[AnswerChoice]
    correct_answer: str
    explanation: str | None = None
    difficulty: Difficulty = Difficulty.MEDIUM


@dataclass
class Quiz:
    id: str
    title: str
    questions: list[Question] = field(default_factory=list)
    source_document_id: str | None = None
    description: str | None = None
    is_published: bool = False


@dataclass
class QuizAnswer:
    question_id: str
    selected_answer: str


@dataclass
class QuizSession:
    id: str
    quiz_id: str
    question_order: list[str]
    answers: dict[str, str] = field(default_factory=dict)
    status: QuizSessionStatus = QuizSessionStatus.ACTIVE
    started_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    completed_at: datetime | None = None