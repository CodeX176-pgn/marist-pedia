from pathlib import Path

import pytest
from app.services.document_service import (
    DocumentUploadError,
    validate_extension,
    validate_file_content,
    validate_filename,
)


def test_path_traversal_filename_is_reduced_to_basename() -> None:
    filename = validate_filename(
        "../../private/lesson.txt"
    )

    assert filename == "lesson.txt"


def test_null_byte_filename_is_rejected() -> None:
    with pytest.raises(DocumentUploadError):
        validate_filename("lesson.txt\x00.exe")


def test_empty_filename_is_rejected() -> None:
    with pytest.raises(DocumentUploadError):
        validate_filename("")


def test_unsupported_extension_is_rejected() -> None:
    with pytest.raises(DocumentUploadError):
        validate_extension("malware.exe")


def test_pdf_content_is_validated(tmp_path: Path) -> None:
    pdf_file = tmp_path / "lesson.pdf"

    pdf_file.write_bytes(b"%PDF-1.7\n")

    validate_file_content(
        pdf_file,
        ".pdf",
    )


def test_fake_pdf_is_rejected(tmp_path: Path) -> None:
    fake_pdf = tmp_path / "lesson.pdf"

    fake_pdf.write_text(
        "This is not actually a PDF.",
        encoding="utf-8",
    )

    with pytest.raises(DocumentUploadError):
        validate_file_content(
            fake_pdf,
            ".pdf",
        )


def test_valid_text_file_is_accepted(tmp_path: Path) -> None:
    text_file = tmp_path / "lesson.txt"

    text_file.write_text(
        "Photosynthesis converts light energy.",
        encoding="utf-8",
    )

    validate_file_content(
        text_file,
        ".txt",
    )


def test_invalid_utf8_text_file_is_rejected(tmp_path: Path) -> None:
    text_file = tmp_path / "lesson.txt"

    text_file.write_bytes(
        b"\xff\xfe\xfa\xfb"
    )

    with pytest.raises(DocumentUploadError):
        validate_file_content(
            text_file,
            ".txt",
        )
