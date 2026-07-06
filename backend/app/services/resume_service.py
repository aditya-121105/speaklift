# backend/app/services/resume_service.py
"""
Resume service — all business logic for the Resume domain.

Responsibilities
----------------
- Validate uploaded file (type, size)
- Generate a storage-safe filename
- Delegate file persistence to StorageBackend (via DI)
- Create / retrieve / delete Resume records via ResumeRepository

Does NOT
--------
- Parse resume content (Sprint C.2)
- Extract skills or experience (Sprint C.2)
- Call spaCy, LLMs, or embeddings

Future architecture
-------------------
Resume
    │
    ▼
Resume Parser  (Sprint C.2)
    │
    ▼
Candidate Profile
    │
    ▼
Interview Context Builder
"""

import logging
import uuid
from pathlib import PurePosixPath
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.storage import StorageBackend
from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.shared.enums import ParsingStatus, StorageProvider, UploadStatus
from app.shared.exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    ResumeNotFoundError,
    ResumeUploadError,
)

from app.ai.document_processing.services import DocumentExtractionService
from app.ai.nlp.pipeline import NLPPipeline
from app.ai.nlp.validators.entity_validator import EntityValidator
from app.services.candidate_profile.builder import CandidateProfileBuilder

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Accepted MIME types mapped to their canonical file extensions.
ACCEPTED_MIME_TYPES: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _storage_provider_from_settings() -> StorageProvider:
    """Map the STORAGE_BACKEND setting to the StorageProvider enum value."""
    mapping: dict[str, StorageProvider] = {
        "local": StorageProvider.LOCAL,
        "s3": StorageProvider.S3,
        "azure": StorageProvider.AZURE,
        "gcs": StorageProvider.GCS,
    }
    return mapping.get(settings.STORAGE_BACKEND.lower(), StorageProvider.LOCAL)


class ResumeService:

    @staticmethod
    def upload_resume(
        db: Session,
        user_id: int,
        filename: str,
        content_type: str | None,
        file_data: bytes,
        storage: StorageBackend,
        document_extractor: DocumentExtractionService,
        nlp_pipeline: NLPPipeline,
        entity_validator: EntityValidator,
        profile_builder: CandidateProfileBuilder,
    ) -> Resume:
        """
        Validate, store, and register a resume file.

        Parameters
        ----------
        db           : active database session
        user_id      : authenticated user's id
        filename     : original filename from the upload
        content_type : MIME type from the multipart header
        file_data    : raw file bytes (already read by the endpoint)
        storage      : injected storage backend

        Returns
        -------
        The created Resume ORM instance.

        Raises
        ------
        InvalidFileTypeError  if content_type is not in ACCEPTED_MIME_TYPES
        FileTooLargeError     if file exceeds MAX_RESUME_SIZE_MB
        ResumeUploadError     if the storage layer fails to persist the file
        """
        # ------------------------------------------------------------------
        # 1. Validate content type
        # ------------------------------------------------------------------
        mime = (content_type or "").lower().strip()
        if mime not in ACCEPTED_MIME_TYPES:
            raise InvalidFileTypeError(
                f"Received '{mime}'. "
                "Accepted types: application/pdf, "
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        # ------------------------------------------------------------------
        # 2. Validate extension (double-check against filename)
        # ------------------------------------------------------------------
        extension = ACCEPTED_MIME_TYPES[mime]
        if filename:
            original_ext = PurePosixPath(filename).suffix.lower()
            if original_ext and original_ext not in ACCEPTED_MIME_TYPES.values():
                raise InvalidFileTypeError(
                    f"File extension '{original_ext}' is not accepted. "
                    "Accepted: .pdf, .docx"
                )

        # ------------------------------------------------------------------
        # 3. Validate file size
        # ------------------------------------------------------------------
        max_bytes = settings.MAX_RESUME_SIZE_MB * 1024 * 1024
        if len(file_data) > max_bytes:
            raise FileTooLargeError(
                f"File is {len(file_data):,} bytes. "
                f"Maximum allowed: {settings.MAX_RESUME_SIZE_MB} MB "
                f"({max_bytes:,} bytes)."
            )

        if len(file_data) == 0:
            raise InvalidFileTypeError("Uploaded file is empty.")

        # ------------------------------------------------------------------
        # 4. Generate storage-safe filename and path
        # ------------------------------------------------------------------
        stored_filename = f"{uuid.uuid4().hex}{extension}"

        # Logical path is provider-agnostic: same string becomes S3 key later.
        storage_path = str(
            PurePosixPath("resumes") / str(user_id) / stored_filename
        )

        # ------------------------------------------------------------------
        # 5. Persist file via the injected storage backend
        # ------------------------------------------------------------------
        try:
            storage.save(file_data, storage_path)
        except OSError as exc:
            logger.error(
                "Storage write failed for user_id=%d path=%s: %s",
                user_id,
                storage_path,
                exc,
            )
            raise ResumeUploadError(
                "Failed to store the resume file. Please try again."
            ) from exc

        # ------------------------------------------------------------------
        # 6. Create database record
        # ------------------------------------------------------------------
        resume = Resume(
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

        resume = ResumeRepository.create(db, resume)

        # ------------------------------------------------------------------
        # 7. Orchestrate AI Pipeline
        # ------------------------------------------------------------------
        try:
            doc_content = document_extractor.extract(file_data, resume.original_filename, mime)
            extracted_entities = nlp_pipeline.run(doc_content)
            validated_entities = entity_validator.validate_entities(extracted_entities)
            candidate_profile = profile_builder.build(validated_entities)
            
            # Profile persistence is out of scope for this sprint.
            
            resume.parsing_status = ParsingStatus.COMPLETED
            resume.parsed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Successfully processed resume {resume.id}")
            
        except Exception as exc:
            logger.exception(f"Pipeline orchestration failed for resume {resume.id}: {exc}")
            resume.parsing_status = ParsingStatus.FAILED
            db.commit()

        return resume

    @staticmethod
    def get_resume(
        db: Session,
        resume_id: int,
        user_id: int,
    ) -> Resume:
        """
        Return a resume belonging to user_id.

        Raises ResumeNotFoundError if the record does not exist or belongs to
        a different user (ownership enforcement via repository).
        """
        resume = ResumeRepository.get_by_id_and_user(db, resume_id, user_id)
        if not resume:
            raise ResumeNotFoundError()
        return resume

    @staticmethod
    def get_user_resumes(
        db: Session,
        user_id: int,
    ) -> list[Resume]:
        """Return all resumes for user_id ordered by upload date descending."""
        return ResumeRepository.get_by_user(db, user_id)

    @staticmethod
    def delete_resume(
        db: Session,
        resume_id: int,
        user_id: int,
        storage: StorageBackend,
    ) -> None:
        """
        Delete the file from storage and the record from the database.

        Storage deletion is attempted first. If it fails, the database record
        is still deleted to avoid orphaned DB rows. Orphaned files can be
        garbage-collected by a future cleanup job.

        Raises ResumeNotFoundError if the resume does not exist or does not
        belong to user_id.
        """
        resume = ResumeService.get_resume(db, resume_id, user_id)

        # Delete file first. Log warning if it fails but do not abort.
        try:
            storage.delete(resume.storage_path)
        except OSError as exc:
            logger.warning(
                "Storage delete failed for path=%s: %s. "
                "Proceeding with DB deletion.",
                resume.storage_path,
                exc,
            )

        ResumeRepository.delete(db, resume)
        logger.info(
            "Deleted resume id=%d for user_id=%d",
            resume_id,
            user_id,
        )
