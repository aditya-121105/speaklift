# backend/app/schemas/job_description.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import ParsingStatus, StorageProvider, UploadStatus


class JobDescriptionResponse(BaseModel):
    """Full JD metadata response."""

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

    uploaded_at: datetime = Field(validation_alias="created_at")
    parsed_at: datetime | None


class JobDescriptionListResponse(BaseModel):
    """Paginated list of JD metadata records."""

    model_config = ConfigDict(from_attributes=True)

    job_descriptions: list[JobDescriptionResponse]
    total: int
