from unittest.mock import MagicMock
import pytest

from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.shared.enums import ParsingStatus, UploadStatus
from app.services.resume_service import ResumeService
from app.core.storage import StorageBackend
from app.ai.document_processing.services import DocumentExtractionService
from app.ai.nlp.pipeline import NLPPipeline
from app.ai.nlp.validators.entity_validator import EntityValidator
from app.services.candidate_profile.builder import CandidateProfileBuilder


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def mock_storage():
    storage = MagicMock(spec=StorageBackend)
    return storage


@pytest.fixture
def mock_document_extractor():
    extractor = MagicMock(spec=DocumentExtractionService)
    extractor.extract.return_value = MagicMock()
    return extractor


@pytest.fixture
def mock_nlp_pipeline():
    pipeline = MagicMock(spec=NLPPipeline)
    pipeline.run.return_value = MagicMock()
    return pipeline


@pytest.fixture
def mock_entity_validator():
    validator = MagicMock(spec=EntityValidator)
    validator.validate_entities.return_value = MagicMock()
    return validator


@pytest.fixture
def mock_profile_builder():
    builder = MagicMock(spec=CandidateProfileBuilder)
    builder.build.return_value = MagicMock()
    return builder


def test_upload_resume_successful_orchestration(
    mock_db, mock_storage, mock_document_extractor, mock_nlp_pipeline,
    mock_entity_validator, mock_profile_builder, monkeypatch
):
    # Mock ResumeRepository.create to just return the object passed
    def mock_create(db, resume):
        resume.id = 1
        return resume

    import app.repositories.resume_repository as repo
    monkeypatch.setattr(repo.ResumeRepository, "create", mock_create)

    resume = ResumeService.upload_resume(
        db=mock_db,
        user_id=1,
        filename="test.pdf",
        content_type="application/pdf",
        file_data=b"dummy",
        storage=mock_storage,
        document_extractor=mock_document_extractor,
        nlp_pipeline=mock_nlp_pipeline,
        entity_validator=mock_entity_validator,
        profile_builder=mock_profile_builder,
    )

    assert resume.parsing_status == ParsingStatus.COMPLETED
    assert resume.upload_status == UploadStatus.COMPLETED

    mock_document_extractor.extract.assert_called_once()
    mock_nlp_pipeline.run.assert_called_once()
    mock_entity_validator.validate_entities.assert_called_once()
    mock_profile_builder.build.assert_called_once()
    mock_db.commit.assert_called()


def test_upload_resume_extraction_failure(
    mock_db, mock_storage, mock_document_extractor, mock_nlp_pipeline,
    mock_entity_validator, mock_profile_builder, monkeypatch
):
    def mock_create(db, resume):
        resume.id = 1
        return resume
    
    import app.repositories.resume_repository as repo
    monkeypatch.setattr(repo.ResumeRepository, "create", mock_create)

    # Force extraction failure
    mock_document_extractor.extract.side_effect = Exception("Extraction failed")

    resume = ResumeService.upload_resume(
        db=mock_db,
        user_id=1,
        filename="test.pdf",
        content_type="application/pdf",
        file_data=b"dummy",
        storage=mock_storage,
        document_extractor=mock_document_extractor,
        nlp_pipeline=mock_nlp_pipeline,
        entity_validator=mock_entity_validator,
        profile_builder=mock_profile_builder,
    )

    assert resume.parsing_status == ParsingStatus.FAILED
    mock_document_extractor.extract.assert_called_once()
    mock_nlp_pipeline.run.assert_not_called()
    mock_db.commit.assert_called()


def test_upload_resume_nlp_failure(
    mock_db, mock_storage, mock_document_extractor, mock_nlp_pipeline,
    mock_entity_validator, mock_profile_builder, monkeypatch
):
    def mock_create(db, resume):
        resume.id = 1
        return resume
    
    import app.repositories.resume_repository as repo
    monkeypatch.setattr(repo.ResumeRepository, "create", mock_create)

    # Force NLP failure
    mock_nlp_pipeline.run.side_effect = Exception("NLP failed")

    resume = ResumeService.upload_resume(
        db=mock_db,
        user_id=1,
        filename="test.pdf",
        content_type="application/pdf",
        file_data=b"dummy",
        storage=mock_storage,
        document_extractor=mock_document_extractor,
        nlp_pipeline=mock_nlp_pipeline,
        entity_validator=mock_entity_validator,
        profile_builder=mock_profile_builder,
    )

    assert resume.parsing_status == ParsingStatus.FAILED
    mock_document_extractor.extract.assert_called_once()
    mock_nlp_pipeline.run.assert_called_once()
    mock_entity_validator.validate_entities.assert_not_called()
    mock_db.commit.assert_called()


def test_upload_resume_validator_failure(
    mock_db, mock_storage, mock_document_extractor, mock_nlp_pipeline,
    mock_entity_validator, mock_profile_builder, monkeypatch
):
    def mock_create(db, resume):
        resume.id = 1
        return resume
    
    import app.repositories.resume_repository as repo
    monkeypatch.setattr(repo.ResumeRepository, "create", mock_create)

    # Force validator failure
    mock_entity_validator.validate_entities.side_effect = Exception("Validation failed")

    resume = ResumeService.upload_resume(
        db=mock_db,
        user_id=1,
        filename="test.pdf",
        content_type="application/pdf",
        file_data=b"dummy",
        storage=mock_storage,
        document_extractor=mock_document_extractor,
        nlp_pipeline=mock_nlp_pipeline,
        entity_validator=mock_entity_validator,
        profile_builder=mock_profile_builder,
    )

    assert resume.parsing_status == ParsingStatus.FAILED
    mock_document_extractor.extract.assert_called_once()
    mock_nlp_pipeline.run.assert_called_once()
    mock_entity_validator.validate_entities.assert_called_once()
    mock_profile_builder.build.assert_not_called()
    mock_db.commit.assert_called()


def test_upload_resume_builder_failure(
    mock_db, mock_storage, mock_document_extractor, mock_nlp_pipeline,
    mock_entity_validator, mock_profile_builder, monkeypatch
):
    def mock_create(db, resume):
        resume.id = 1
        return resume
    
    import app.repositories.resume_repository as repo
    monkeypatch.setattr(repo.ResumeRepository, "create", mock_create)

    # Force builder failure
    mock_profile_builder.build.side_effect = Exception("Builder failed")

    resume = ResumeService.upload_resume(
        db=mock_db,
        user_id=1,
        filename="test.pdf",
        content_type="application/pdf",
        file_data=b"dummy",
        storage=mock_storage,
        document_extractor=mock_document_extractor,
        nlp_pipeline=mock_nlp_pipeline,
        entity_validator=mock_entity_validator,
        profile_builder=mock_profile_builder,
    )

    assert resume.parsing_status == ParsingStatus.FAILED
    mock_profile_builder.build.assert_called_once()
    mock_db.commit.assert_called()
