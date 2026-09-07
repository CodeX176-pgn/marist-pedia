from dataclasses import dataclass, field
from enum import StrEnum


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


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
