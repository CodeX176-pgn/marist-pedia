from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: UUID
    original_filename: str
    stored_filename: str
    extension: str
    size: int
    uploaded_at: datetime
    message: str


class DocumentTextResponse(BaseModel):
    id: UUID
    filename: str
    extension: str
    character_count: int
    text: str


class DocumentChunk(BaseModel):
    index: int
    text: str
    character_count: int


class DocumentProcessingResponse(BaseModel):
    id: UUID
    filename: str
    character_count: int
    chunk_count: int
    chunks: list[DocumentChunk]
