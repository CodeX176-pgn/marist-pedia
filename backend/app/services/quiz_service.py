from uuid import uuid4

from backend.app.models.quiz import Quiz


def create_quiz(
    title: str,
    document_id: str | None = None,
    question_count: int = 5,
) -> Quiz:
    quiz_id = str(uuid4())

    return Quiz(
        id=quiz_id,
        title=title,
        document_id=document_id,
        questions=[],
    )
