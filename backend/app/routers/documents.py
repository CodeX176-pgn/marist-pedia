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

    matching_files = list(
        settings.upload_directory.glob(f"{document_id}.*")
    )

    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    file_path = matching_files[0]
    extension = file_path.suffix.lower()

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
        filename=file_path.name,
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

    matching_files = list(
        settings.upload_directory.glob(f"{document_id}.*")
    )

    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    file_path = matching_files[0]
    extension = file_path.suffix.lower()

    try:
        raw_text = extract_document_text(
            file_path=file_path,
            extension=extension,
        )

        cleaned_text = clean_extracted_text(raw_text)

        chunks = split_into_chunks(cleaned_text)

    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return DocumentProcessingResponse(
        id=document_id,
        filename=file_path.name,
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
