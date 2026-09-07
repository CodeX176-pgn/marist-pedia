import random
import re
from uuid import uuid4

from app.models.quiz import (
    AnswerChoice,
    Difficulty,
    Question,
    Quiz,
)


class QuizService:
    """Generate quizzes from processed document text."""

    def generate_quiz(
        self,
        title: str,
        chunks: list[str],
        question_count: int = 5,
        source_document_id: str | None = None,
    ) -> Quiz:
        """Generate a quiz from document chunks."""

        if not chunks:
            raise ValueError("At least one text chunk is required.")

        if question_count < 1:
            raise ValueError("Question count must be at least 1.")

        sentences = self._extract_sentences(chunks)

        if not sentences:
            raise ValueError("No usable sentences were found.")

        question_count = min(question_count, len(sentences))

        selected_sentences = random.sample(
            sentences,
            question_count,
        )

        questions = [
            self._create_question(sentence, index)
            for index, sentence in enumerate(selected_sentences, start=1)
        ]

        return Quiz(
            id=str(uuid4()),
            title=title,
            questions=questions,
            source_document_id=source_document_id,
        )

    def _extract_sentences(self, chunks: list[str]) -> list[str]:
        """Extract usable sentences from processed text."""

        sentences: list[str] = []

        for chunk in chunks:
            parts = re.split(r"(?<=[.!?])\s+", chunk.strip())

            for sentence in parts:
                sentence = " ".join(sentence.split())

                if self._is_usable_sentence(sentence):
                    sentences.append(sentence)

        return sentences

    def _is_usable_sentence(self, sentence: str) -> bool:
        """Determine whether a sentence can produce a question."""

        words = sentence.split()

        if len(words) < 5:
            return False

        if len(sentence) > 300:
            return not len(sentence) > 300

        return True

    def _create_question(
        self,
        sentence: str,
        index: int,
    ) -> Question:
        """Create an MCQ from a sentence."""

        answer = self._select_answer_phrase(sentence)

        question_text = self._create_question_text(
            sentence,
            answer,
        )

        choices = self._create_choices(answer)

        return Question(
            id=str(uuid4()),
            text=question_text,
            choices=choices,
            correct_answer="A",
            explanation=(
                f"The correct answer is based on the source statement: "
                f'"{sentence}"'
            ),
            difficulty=Difficulty.MEDIUM,
        )

    def _select_answer_phrase(self, sentence: str) -> str:
        """Select a phrase from the sentence to turn into the answer."""

        words = sentence.split()

        if len(words) <= 8:
            return " ".join(words[-2:]).rstrip(".,!?")

        # Prefer the middle portion of longer sentences.
        start = max(1, len(words) // 3)
        end = min(start + 4, len(words) - 1)

        phrase = " ".join(words[start:end])

        return phrase.rstrip(".,!?")

    def _create_question_text(
        self,
        sentence: str,
        answer: str,
    ) -> str:
        """Create a fill-in-the-blank style MCQ."""

        escaped_answer = re.escape(answer)

        question = re.sub(
            escaped_answer,
            "_____",
            sentence,
            count=1,
            flags=re.IGNORECASE,
        )

        if question == sentence:
            question = f"Which phrase correctly completes this statement?\n\n{sentence}"

        return question

    def _create_choices(
        self,
        correct_answer: str,
    ) -> list[AnswerChoice]:
        """Create answer choices."""

        distractors = [
            "an unrelated concept",
            "a different process",
            "another type of system",
        ]

        choices = [
            AnswerChoice(
                id="A",
                text=correct_answer,
            ),
            AnswerChoice(
                id="B",
                text=distractors[0],
            ),
            AnswerChoice(
                id="C",
                text=distractors[1],
            ),
            AnswerChoice(
                id="D",
                text=distractors[2],
            ),
        ]

        return choices
