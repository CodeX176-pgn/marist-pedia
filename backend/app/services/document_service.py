from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from backend.app.config.settings import settings


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


def validate_extension(filename: str) -> str:
    """Validate and return the file extension."""

    extension = get_extension(filename)

    if extension not in settings.allowed_document_extensions:
        allowed = ", ".join(settings.allowed_document_extensions)

        raise DocumentUploadError(
            f"Unsupported file type. Allowed types: {allowed}"
        )

    return extension


async def save_document(file: UploadFile) -> dict:
    """Validate and safely save an uploaded document."""

    if not file.filename:
        raise DocumentUploadError("The uploaded file has no filename.")

    extension = validate_extension(file.filename)

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

    except Exception:
        if destination.exists():
            destination.unlink()

        raise

    if total_size == 0:
        if destination.exists():
            destination.unlink()

        raise DocumentUploadError("The uploaded file is empty.")

    return {
        "id": document_id,
        "original_filename": Path(file.filename).name,
        "stored_filename": stored_filename,
        "extension": extension,
        "size": total_size,
        "uploaded_at": datetime.now(UTC),
    }
