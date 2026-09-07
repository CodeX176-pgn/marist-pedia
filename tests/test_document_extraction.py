from pathlib import Path

import pytest
from app.services.document_extraction_service import (
    DocumentExtractionError,
    extract_document_text,
)


def test_extract_txt_file(tmp_path: Path) -> None:
    document = tmp_path / "lesson.txt"

    document.write_text(
        "Photosynthesis converts light energy into chemical energy.",
        encoding="utf-8",
    )

    text = extract_document_text(
        document,
        ".txt",
    )

    assert "Photosynthesis" in text
    assert "chemical energy" in text


def test_extract_markdown_file(tmp_path: Path) -> None:
    document = tmp_path / "lesson.md"

    document.write_text(
        "# Photosynthesis\n\nPlants use sunlight.",
        encoding="utf-8",
    )

    text = extract_document_text(
        document,
        ".md",
    )

    assert "# Photosynthesis" in text
    assert "Plants use sunlight." in text


def test_empty_document_is_rejected(tmp_path: Path) -> None:
    document = tmp_path / "empty.txt"

    document.write_text("", encoding="utf-8")

    with pytest.raises(DocumentExtractionError):
        extract_document_text(
            document,
            ".txt",
        )


def test_unsupported_extension_is_rejected(tmp_path: Path) -> None:
    document = tmp_path / "program.exe"

    document.write_text(
        "not a supported document",
        encoding="utf-8",
    )

    with pytest.raises(DocumentExtractionError):
        extract_document_text(
            document,
            ".exe",
        )
