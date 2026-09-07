from pathlib import Path

from pypdf import PdfReader


class DocumentExtractionError(Exception):
    """Raised when document text cannot be extracted."""


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from all pages of a PDF."""

    try:
        reader = PdfReader(file_path)

        pages: list[str] = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n\n".join(pages)

    except Exception as exc:
        raise DocumentExtractionError(
            f"Could not extract text from PDF: {exc}"
        ) from exc


def extract_text_from_text_file(file_path: Path) -> str:
    """Read text from TXT or Markdown files."""

    try:
        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except OSError as exc:
        raise DocumentExtractionError(
            f"Could not read document: {exc}"
        ) from exc


def extract_document_text(
    file_path: Path,
    extension: str,
) -> str:
    """Extract text from a supported document."""

    normalized_extension = extension.lower()

    if normalized_extension == ".pdf":
        text = extract_text_from_pdf(file_path)

    elif normalized_extension in {".txt", ".md", ".markdown"}:
        text = extract_text_from_text_file(file_path)

    else:
        raise DocumentExtractionError(
            f"Unsupported document extension: {extension}"
        )

    if not text.strip():
        raise DocumentExtractionError(
            "The document does not contain extractable text."
        )

    return text
