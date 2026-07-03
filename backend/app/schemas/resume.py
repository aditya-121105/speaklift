# backend/app/schemas/resume.py
"""
Resume Pydantic schemas.

ResumeResponse       — returned by upload, GET, and list endpoints.
ResumeListResponse   — wrapper for list endpoints.

Design notes
------------
- `uploaded_at` is mapped from `created_at` (TimestampMixin field).
  No redundant column is added to the model.
- ORM models are never exposed directly.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import ParsingStatus, StorageProvider, UploadStatus


class ResumeResponse(BaseModel):
    """Full resume metadata response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    # File identity
    original_filename: str
    stored_filename: str
    file_extension: str
    mime_type: str
    file_size_bytes: int

    # Storage
    storage_provider: StorageProvider
    storage_path: str

    # Status
    upload_status: UploadStatus
    parsing_status: ParsingStatus

    # Timestamps — created_at (TimestampMixin) is exposed as uploaded_at
    uploaded_at: datetime = Field(validation_alias="created_at")
    parsed_at: datetime | None


class ResumeListResponse(BaseModel):
    """Paginated list of resume metadata records."""

    model_config = ConfigDict(from_attributes=True)

    resumes: list[ResumeResponse]
    total: int
