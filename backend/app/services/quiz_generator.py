import random
import re
from collections.abc import Sequence

from app.models.quiz import QuestionDifficulty, QuizQuestion


class QuizGenerationError(Exception):
    """Raised when a quiz cannot be generated from the supplied content."""


class QuizGenerator:
    """Generate basic multiple-choice questions from processed document text."""

    def __init__(self, *, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def generate(
        self,
        text: str,
        question_count: int = 5,
    ) -> list[QuizQuestion]:
        if not text.strip():
            raise QuizGenerationError("Cannot generate questions from empty text.")

        if question_count < 1:
            raise ValueError("question_count must be at least 1.")

        sentences = self._extract_candidate_sentences(text)

        if not sentences:
            raise QuizGenerationError(
                "The document does not contain enough usable content "
                "to generate questions."
            )

        questions: list[QuizQuestion] = []

        for sentence in sentences:
            if len(questions) >= question_count:
                break

            question = self._generate_from_sentence(
                sentence,
                sentences,
            )

            if question is not None:
                questions.append(question)

        if not questions:
            raise QuizGenerationError(
                "No suitable questions could be generated from the document."
            )

        return questions

    def _extract_candidate_sentences(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text).strip()

        sentences = re.split(r"(?<=[.!?])\s+", normalized)

        return [
            sentence.strip()
            for sentence in sentences
            if self._is_useful_sentence(sentence)
        ]

    @staticmethod
    def _is_useful_sentence(sentence: str) -> bool:
        words = sentence.split()

        if len(words) < 8:
            return False

        if len(words) > 50:
            return False

        return sentence.endswith((".", "!", "?"))

    def _generate_from_sentence(
        self,
        sentence: str,
        all_sentences: Sequence[str],
    ) -> QuizQuestion | None:
        match = re.search(
            r"\b([A-Z][A-Za-z-]{2,}|[0-9]{2,4})\b",
            sentence,
        )

        if match is None:
            return None

        answer = match.group(1)

        question_prompt = sentence.replace(
            answer,
            "_____",
            1,
        )

        distractors = self._find_distractors(
            answer,
            all_sentences,
        )

        if len(distractors) < 3:
            return None

        choices = [answer, *distractors[:3]]
        self._rng.shuffle(choices)

        return QuizQuestion(
            prompt=f"Which answer correctly completes the statement?\n\n"
            f"{question_prompt}",
            choices=choices,
            correct_answer=answer,
            explanation=f"The document states: {sentence}",
            difficulty=QuestionDifficulty.EASY,
        )

    @staticmethod
    def _find_distractors(
        answer: str,
        sentences: Sequence[str],
    ) -> list[str]:
        candidates: list[str] = []

        for sentence in sentences:
            matches = re.findall(
                r"\b(?:[A-Z][A-Za-z-]{2,}|[0-9]{2,4})\b",
                sentence,
            )

            for candidate in matches:
                if candidate.lower() == answer.lower():
                    continue

                if candidate not in candidates:
                    candidates.append(candidate)

        return candidates
    