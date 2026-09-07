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
