from dataclasses import dataclass, field


@dataclass
class Question:
    id: str
    question: str
    options: list[str]
    correct_answer: str
    explanation: str | None = None


@dataclass
class Quiz:
    id: str
    title: str
    document_id: str | None = None
    questions: list[Question] = field(default_factory=list)
