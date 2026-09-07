import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str
    character_count: int


def normalize_unicode(text: str) -> str:
    """Normalize Unicode characters into a consistent representation."""

    return unicodedata.normalize("NFKC", text)


def normalize_whitespace(text: str) -> str:
    """Normalize excessive spaces, tabs, and blank lines."""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize whitespace on each line.
    text = "\n".join(
        line.strip()
        for line in text.splitlines()
    )

    # Collapse repeated spaces and tabs.
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse more than two consecutive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_extracted_text(text: str) -> str:
    """Clean extracted document text for downstream processing."""

    text = normalize_unicode(text)

    # Remove control characters while preserving newlines and tabs.
    text = "".join(
        character
        for character in text
        if character in {"\n", "\t"}
        or not unicodedata.category(character).startswith("C")
    )

    return normalize_whitespace(text)


def split_into_chunks(
    text: str,
    max_characters: int = 2000,
    overlap: int = 200,
) -> list[TextChunk]:
    """
    Split text into manageable overlapping chunks.

    Chunks prefer paragraph boundaries and fall back to sentence
    boundaries when a paragraph is too large.
    """

    if max_characters <= 0:
        raise ValueError("max_characters must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= max_characters:
        raise ValueError(
            "overlap must be smaller than max_characters."
        )

    cleaned_text = clean_extracted_text(text)

    if not cleaned_text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", cleaned_text)
        if paragraph.strip()
    ]

    chunks: list[TextChunk] = []
    current_parts: list[str] = []
    current_length = 0

    def add_chunk(chunk_text: str) -> None:
        chunks.append(
            TextChunk(
                index=len(chunks),
                text=chunk_text,
                character_count=len(chunk_text),
            )
        )

    for paragraph in paragraphs:
        if len(paragraph) > max_characters:
            sentences = re.split(
                r"(?<=[.!?])\s+",
                paragraph,
            )

            for sentence in sentences:
                sentence = sentence.strip()

                if not sentence:
                    continue

                if (
                    current_length
                    and current_length + len(sentence) + 1
                    > max_characters
                ):
                    chunk_text = " ".join(current_parts).strip()

                    if chunk_text:
                        add_chunk(chunk_text)

                    overlap_text = (
                        chunk_text[-overlap:]
                        if overlap
                        else ""
                    )

                    current_parts = (
                        [overlap_text]
                        if overlap_text
                        else []
                    )

                    current_length = len(overlap_text)

                current_parts.append(sentence)
                current_length += len(sentence) + 1

            continue

        additional_length = (
            len(paragraph)
            if not current_parts
            else len(paragraph) + 2
        )

        if (
            current_parts
            and current_length + additional_length
            > max_characters
        ):
            chunk_text = "\n\n".join(
                current_parts
            ).strip()

            if chunk_text:
                add_chunk(chunk_text)

            overlap_text = (
                chunk_text[-overlap:]
                if overlap
                else ""
            )

            current_parts = (
                [overlap_text]
                if overlap_text
                else []
            )

            current_length = len(overlap_text)

        current_parts.append(paragraph)
        current_length += additional_length

    if current_parts:
        chunk_text = "\n\n".join(
            current_parts
        ).strip()

        if chunk_text:
            add_chunk(chunk_text)

    return chunks
