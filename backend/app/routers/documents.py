from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config.settings import settings
from app.schemas.document import (
    DocumentChunk,
    DocumentProcessingResponse,
    DocumentTextResponse,
    DocumentUploadResponse,
)
from app.services.document_extraction_service import (
    DocumentExtractionError,
    extract_document_text,
)
from app.services.document_service import (
    DocumentUploadError,
    get_document,
    save_document,
)
from app.services.text_processing_service import (
    clean_extracted_text,
    split_into_chunks,
)

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: Annotated[UploadFile, File()],
) -> DocumentUploadResponse:
    """Upload a PDF, TXT, or Markdown document."""

    try:
        document = await save_document(file)

    except DocumentUploadError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()

    return DocumentUploadResponse(
        **document,
        message="Document uploaded successfully.",
    )


@router.get(
    "/{document_id}/text",
    response_model=DocumentTextResponse,
)
async def extract_document(
    document_id: UUID,
) -> DocumentTextResponse:
    """Extract text from an uploaded document."""

    # Look up the document metadata in SQLite.
    try:
        document = get_document(document_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        ) from exc

    # Build the path to the actual uploaded file.
    file_path = (
        settings.upload_directory
        / document.stored_filename
    )

    # Make sure the database record points to a real file.
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file is missing from storage.",
        )

    # Use the extension stored in the database.
    extension = document.extension

    try:
        text = extract_document_text(
            file_path=file_path,
            extension=extension,
        )

    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return DocumentTextResponse(
        id=document_id,
        filename=document.original_filename,
        extension=extension,
        character_count=len(text),
        text=text,
    )


@router.get(
    "/{document_id}/process",
    response_model=DocumentProcessingResponse,
)
async def process_document(
    document_id: UUID,
) -> DocumentProcessingResponse:
    """Extract, clean, and chunk an uploaded document."""

    # Look up the document metadata in SQLite.
    try:
        document = get_document(document_id)

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        ) from exc

    # Build the path to the actual uploaded file.
    file_path = (
        settings.upload_directory
        / document.stored_filename
    )

    # Make sure the database record points to a real file.
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file is missing from storage.",
        )

    # Use the extension stored in the database.
    extension = document.extension

    try:
        # Extract the original text from the document.
        raw_text = extract_document_text(
            file_path=file_path,
            extension=extension,
        )

        # Remove unnecessary whitespace and noise.
        cleaned_text = clean_extracted_text(
            raw_text
        )

        # Split the cleaned text into manageable chunks.
        chunks = split_into_chunks(
            cleaned_text
        )

    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return DocumentProcessingResponse(
        id=document_id,
        filename=document.original_filename,
        character_count=len(cleaned_text),
        chunk_count=len(chunks),
        chunks=[
            DocumentChunk(
                index=chunk.index,
                text=chunk.text,
                character_count=chunk.character_count,
            )
            for chunk in chunks
        ],
    )
