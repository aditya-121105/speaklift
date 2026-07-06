import pytest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session
from app.models.job_description import JobDescription
from app.shared.enums import ParsingStatus, UploadStatus, StorageProvider
from app.services.job_description_service import (
    JobDescriptionService,
    JobDescriptionUploadError,
    JobDescriptionNotFoundError,
)
from app.shared.exceptions import InvalidFileTypeError, FileTooLargeError
from app.core.storage import StorageBackend
from app.ai.document_processing.services import DocumentExtractionService


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_storage():
    return MagicMock(spec=StorageBackend)

@pytest.fixture
def mock_extractor():
    extractor = MagicMock(spec=DocumentExtractionService)
    extractor.extract.return_value = MagicMock()
    return extractor

def test_upload_jd_successful_orchestration(mock_db, mock_storage, mock_extractor, monkeypatch):
    def mock_create(db, jd):
        jd.id = 1
        return jd
    
    import app.repositories.job_description_repository as repo
    monkeypatch.setattr(repo.JobDescriptionRepository, "create", mock_create)

    jd = JobDescriptionService.upload_job_description(
        db=mock_db,
        user_id=1,
        filename="job.pdf",
        content_type="application/pdf",
        file_data=b"dummy content",
        storage=mock_storage,
        document_extractor=mock_extractor,
    )

    assert jd.parsing_status == ParsingStatus.COMPLETED
    assert jd.upload_status == UploadStatus.COMPLETED
    assert getattr(jd, "parsed_at", None) is not None
    assert jd.mime_type == "application/pdf"

    mock_storage.save.assert_called_once()
    mock_extractor.extract.assert_called_once()
    mock_db.commit.assert_called()

def test_upload_jd_invalid_file(mock_db, mock_storage, mock_extractor):
    with pytest.raises(InvalidFileTypeError):
        JobDescriptionService.upload_job_description(
            db=mock_db,
            user_id=1,
            filename="image.png",
            content_type="image/png",
            file_data=b"...",
            storage=mock_storage,
            document_extractor=mock_extractor,
        )

def test_upload_jd_storage_failure(mock_db, mock_storage, mock_extractor):
    mock_storage.save.side_effect = OSError("Disk full")

    with pytest.raises(JobDescriptionUploadError):
        JobDescriptionService.upload_job_description(
            db=mock_db,
            user_id=1,
            filename="job.pdf",
            content_type="application/pdf",
            file_data=b"dummy",
            storage=mock_storage,
            document_extractor=mock_extractor,
        )

def test_upload_jd_extraction_failure(mock_db, mock_storage, mock_extractor, monkeypatch):
    def mock_create(db, jd):
        jd.id = 1
        return jd
    
    import app.repositories.job_description_repository as repo
    monkeypatch.setattr(repo.JobDescriptionRepository, "create", mock_create)

    mock_extractor.extract.side_effect = Exception("Extraction failed")

    jd = JobDescriptionService.upload_job_description(
        db=mock_db,
        user_id=1,
        filename="job.pdf",
        content_type="application/pdf",
        file_data=b"dummy",
        storage=mock_storage,
        document_extractor=mock_extractor,
    )

    assert jd.parsing_status == ParsingStatus.FAILED
    assert getattr(jd, "parsed_at", None) is None
    mock_extractor.extract.assert_called_once()
    mock_db.commit.assert_called()
