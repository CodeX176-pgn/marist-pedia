from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config.settings import settings


class DocumentUploadError(Exception):
    """Raised when a document cannot be uploaded safely."""


def get_extension(filename: str) -> str:
    """Return a normalized lowercase file extension."""

    extension = Path(filename).suffix.lower()

    if not extension:
        raise DocumentUploadError(
            "The uploaded file must have a supported file extension."
        )

    return extension


def validate_filename(filename: str) -> str:
    """Validate a user-supplied filename and return its safe basename."""

    if not filename:
        raise DocumentUploadError(
            "The uploaded file has no filename."
        )

    if "\x00" in filename:
        raise DocumentUploadError(
            "The filename contains an invalid character."
        )

    if len(filename) > settings.max_filename_length:
        raise DocumentUploadError(
            "The filename is too long."
        )

    safe_filename = Path(filename).name

    if not safe_filename:
        raise DocumentUploadError(
            "The uploaded file has an invalid filename."
        )

    if any(ord(character) < 32 for character in safe_filename):
        raise DocumentUploadError(
            "The filename contains invalid control characters."
        )

    return safe_filename


def validate_extension(filename: str) -> str:
    """Validate and return the file extension."""

    extension = get_extension(filename)

    if extension not in settings.allowed_document_extensions:
        allowed = ", ".join(settings.allowed_document_extensions)

        raise DocumentUploadError(
            f"Unsupported file type. Allowed types: {allowed}"
        )

    return extension


def validate_file_content(
    file_path: Path,
    extension: str,
) -> None:
    """Validate that the stored file matches its declared type."""

    try:
        with file_path.open("rb") as input_file:
            first_bytes = input_file.read(8)

    except OSError as exc:
        raise DocumentUploadError(
            "Could not validate the uploaded file."
        ) from exc

    if extension == ".pdf":
        if not first_bytes.startswith(b"%PDF-"):
            raise DocumentUploadError(
                "The uploaded file is not a valid PDF."
            )

        return

    # TXT and Markdown files should contain valid UTF-8 text.
    try:
        with file_path.open("rb") as input_file:
            while chunk := input_file.read(1024 * 1024):
                chunk.decode("utf-8")

    except UnicodeDecodeError as exc:
        raise DocumentUploadError(
            "The uploaded text file is not valid UTF-8 text."
        ) from exc

    except OSError as exc:
        raise DocumentUploadError(
            "Could not validate the uploaded file."
        ) from exc


async def save_document(file: UploadFile) -> dict:
    """Validate and safely save an uploaded document."""

    if not file.filename:
        raise DocumentUploadError(
            "The uploaded file has no filename."
        )

    safe_filename = validate_filename(file.filename)
    extension = validate_extension(safe_filename)

    document_id = uuid4()
    stored_filename = f"{document_id}{extension}"

    settings.upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = settings.upload_directory / stored_filename
    total_size = 0

    try:
        with destination.open("wb") as output_file:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > settings.max_upload_size:
                    raise DocumentUploadError(
                        "The uploaded file exceeds the maximum size of "
                        f"{settings.max_upload_size // (1024 * 1024)} MB."
                    )

                output_file.write(chunk)

        if total_size == 0:
            raise DocumentUploadError(
                "The uploaded file is empty."
            )

        validate_file_content(
            destination,
            extension,
        )

    except Exception:
        if destination.exists():
            destination.unlink()

        raise

    return {
        "id": document_id,
        "original_filename": safe_filename,
        "stored_filename": stored_filename,
        "extension": extension,
        "size": total_size,
        "uploaded_at": datetime.now(UTC),
    }
