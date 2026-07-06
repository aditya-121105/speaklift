# backend/app/services/job_description_service.py
import logging
import uuid
from pathlib import PurePosixPath
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.storage import StorageBackend
from app.models.job_description import JobDescription
from app.repositories.job_description_repository import JobDescriptionRepository
from app.shared.enums import ParsingStatus, StorageProvider, UploadStatus
from app.shared.exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
)

from app.ai.document_processing.services import DocumentExtractionService

logger = logging.getLogger(__name__)

ACCEPTED_MIME_TYPES: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",  # Often JDs are just copy-pasted text
}

def _storage_provider_from_settings() -> StorageProvider:
    mapping: dict[str, StorageProvider] = {
        "local": StorageProvider.LOCAL,
        "s3": StorageProvider.S3,
        "azure": StorageProvider.AZURE,
        "gcs": StorageProvider.GCS,
    }
    return mapping.get(settings.STORAGE_BACKEND.lower(), StorageProvider.LOCAL)

class JobDescriptionUploadError(Exception):
    pass

class JobDescriptionNotFoundError(Exception):
    pass

class JobDescriptionService:
    @staticmethod
    def upload_job_description(
        db: Session,
        user_id: int,
        filename: str,
        content_type: str | None,
        file_data: bytes,
        storage: StorageBackend,
        document_extractor: DocumentExtractionService,
    ) -> JobDescription:
        mime = (content_type or "").lower().strip()
        if mime not in ACCEPTED_MIME_TYPES:
            raise InvalidFileTypeError(f"Received '{mime}'. Accepted types: pdf, docx, txt")

        extension = ACCEPTED_MIME_TYPES[mime]
        max_bytes = settings.MAX_RESUME_SIZE_MB * 1024 * 1024
        if len(file_data) > max_bytes:
            raise FileTooLargeError(f"File too large. Maximum allowed: {settings.MAX_RESUME_SIZE_MB} MB")

        if len(file_data) == 0:
            raise InvalidFileTypeError("Uploaded file is empty.")

        stored_filename = f"{uuid.uuid4().hex}{extension}"
        storage_path = str(PurePosixPath("job_descriptions") / str(user_id) / stored_filename)

        try:
            storage.save(file_data, storage_path)
        except OSError as exc:
            logger.error(f"Storage write failed: {exc}")
            raise JobDescriptionUploadError("Failed to store the JD file.") from exc

        job_description = JobDescription(
            user_id=user_id,
            original_filename=filename or stored_filename,
            stored_filename=stored_filename,
            file_extension=extension,
            mime_type=mime,
            file_size_bytes=len(file_data),
            storage_provider=_storage_provider_from_settings(),
            storage_path=storage_path,
            upload_status=UploadStatus.COMPLETED,
            parsing_status=ParsingStatus.PROCESSING,
        )

        job_description = JobDescriptionRepository.create(db, job_description)

        try:
            doc_content = document_extractor.extract(file_data, job_description.original_filename, mime)
            # Stop after DocumentContent extraction for now
            job_description.parsing_status = ParsingStatus.COMPLETED
            job_description.parsed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Successfully processed JD {job_description.id}")
        except Exception as exc:
            logger.exception(f"Pipeline extraction failed for JD {job_description.id}: {exc}")
            job_description.parsing_status = ParsingStatus.FAILED
            db.commit()

        return job_description

    @staticmethod
    def get_job_description(db: Session, job_description_id: int, user_id: int) -> JobDescription:
        jd = JobDescriptionRepository.get_by_id_and_user(db, job_description_id, user_id)
        if not jd:
            raise JobDescriptionNotFoundError()
        return jd

    @staticmethod
    def delete_job_description(db: Session, job_description_id: int, user_id: int, storage: StorageBackend) -> None:
        jd = JobDescriptionService.get_job_description(db, job_description_id, user_id)
        try:
            storage.delete(jd.storage_path)
        except OSError as exc:
            logger.warning(f"Storage delete failed: {exc}")
        JobDescriptionRepository.delete(db, jd)
