from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.app.schemas.document import DocumentUploadResponse
from backend.app.services.document_service import (
    DocumentUploadError,
    save_document,
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
