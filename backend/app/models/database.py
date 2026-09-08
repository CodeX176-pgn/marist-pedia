from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy database models."""


class DocumentRecord(Base):
    """Store metadata about an uploaded document."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255)
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    extension: Mapped[str] = mapped_column(
        String(20)
    )

    size: Mapped[int] = mapped_column(
        Integer
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )


class QuizRecord(Base):
    """Store a generated quiz."""

    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(200)
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_document_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    # One quiz can contain many questions.
    questions: Mapped[list["QuestionRecord"]] = relationship(
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="QuestionRecord.position",
    )


class QuestionRecord(Base):
    """Store an individual question."""

    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    quiz_id: Mapped[str] = mapped_column(
        ForeignKey(
            "quizzes.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    position: Mapped[int] = mapped_column(
        Integer
    )

    text: Mapped[str] = mapped_column(
        Text
    )

    correct_answer: Mapped[str] = mapped_column(
        String(20)
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    difficulty: Mapped[str] = mapped_column(
        String(20)
    )

    quiz: Mapped[QuizRecord] = relationship(
        back_populates="questions"
    )

    # One question can have many answer choices.
    choices: Mapped[list["AnswerChoiceRecord"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="AnswerChoiceRecord.position",
    )


class AnswerChoiceRecord(Base):
    """Store one possible answer choice."""

    __tablename__ = "answer_choices"

    # A/B/C/D can repeat between questions,
    # so the question ID is also part of the primary key.
    id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    question_id: Mapped[str] = mapped_column(
        ForeignKey(
            "questions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        index=True,
    )

    position: Mapped[int] = mapped_column(
        Integer
    )

    text: Mapped[str] = mapped_column(
        Text
    )

    question: Mapped[QuestionRecord] = relationship(
        back_populates="choices"
    )


class QuizSessionRecord(Base):
    """Store a student's active or completed quiz session."""

    __tablename__ = "quiz_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    quiz_id: Mapped[str] = mapped_column(
        ForeignKey(
            "quizzes.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20)
    )

    # JSON keeps the exact question order used by the session.
    question_order: Mapped[list[str]] = mapped_column(
        JSON
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    answers: Mapped[list["QuizAnswerRecord"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )

    result: Mapped["QuizResultRecord | None"] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        uselist=False,
    )


class QuizAnswerRecord(Base):
    """Store an answer submitted during a quiz session."""

    __tablename__ = "quiz_answers"

    session_id: Mapped[str] = mapped_column(
        ForeignKey(
            "quiz_sessions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    question_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    selected_answer: Mapped[str] = mapped_column(
        String(20)
    )

    session: Mapped[QuizSessionRecord] = relationship(
        back_populates="answers"
    )


class QuizResultRecord(Base):
    """Store the final score for a submitted quiz."""

    __tablename__ = "quiz_results"

    session_id: Mapped[str] = mapped_column(
        ForeignKey(
            "quiz_sessions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    score: Mapped[int] = mapped_column(
        Integer
    )

    total_questions: Mapped[int] = mapped_column(
        Integer
    )

    percentage: Mapped[float] = mapped_column(
        Float
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    session: Mapped[QuizSessionRecord] = relationship(
        back_populates="result"
    )

    items: Mapped[list["QuizResultItemRecord"]] = relationship(
        back_populates="result",
        cascade="all, delete-orphan",
        order_by="QuizResultItemRecord.position",
    )


class QuizResultItemRecord(Base):
    """Store the result for one question."""

    __tablename__ = "quiz_result_items"

    session_id: Mapped[str] = mapped_column(
        ForeignKey(
            "quiz_results.session_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    question_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    position: Mapped[int] = mapped_column(
        Integer
    )

    selected_answer: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    correct_answer: Mapped[str] = mapped_column(
        String(20)
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result: Mapped[QuizResultRecord] = relationship(
        back_populates="items"
    )
