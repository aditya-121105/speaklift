"""
tests/resume/test_resume_service.py

Unit tests for ResumeService.

Strategy
--------
- No real database — all DB calls are patched via MagicMock.
- No real filesystem — storage backend is replaced by a MagicMock.
- Tests cover business logic only (the service layer contract).
- Acceptance criteria from Sprint C.1:
    ✓ Upload works
    ✓ Metadata stored
    ✓ Files saved correctly
    ✓ Ownership enforced
    ✓ Delete removes metadata
    ✓ Delete removes stored file
"""

from unittest.mock import MagicMock, patch

import pytest

from app.models.resume import Resume
from app.services.resume_service import ACCEPTED_MIME_TYPES, ResumeService
from app.shared.enums import ParsingStatus, StorageProvider, UploadStatus
from app.shared.exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    ResumeNotFoundError,
    ResumeUploadError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_resume(
    id: int = 1,
    user_id: int = 42,
    storage_path: str = "resumes/42/abc.pdf",
) -> Resume:
    """Return a partially-constructed Resume ORM instance (no DB)."""
    r = Resume()
    r.id = id
    r.user_id = user_id
    r.original_filename = "my_cv.pdf"
    r.stored_filename = "abc.pdf"
    r.file_extension = ".pdf"
    r.mime_type = "application/pdf"
    r.file_size_bytes = 1024
    r.storage_provider = StorageProvider.LOCAL
    r.storage_path = storage_path
    r.upload_status = UploadStatus.COMPLETED
    r.parsing_status = ParsingStatus.PENDING
    r.parsed_at = None
    return r


def _mock_db() -> MagicMock:
    return MagicMock()


def _mock_storage(save_return: str = "resumes/42/abc.pdf") -> MagicMock:
    storage = MagicMock()
    storage.save.return_value = save_return
    return storage


# ---------------------------------------------------------------------------
# upload_resume — happy path
# ---------------------------------------------------------------------------

class TestUploadResumeHappyPath:

    @patch("app.services.resume_service.ResumeRepository.create")
    def test_upload_pdf_succeeds(self, mock_create: MagicMock) -> None:
        """A valid PDF upload stores the file and persists the DB record."""
        db = _mock_db()
        storage = _mock_storage()
        file_data = b"%PDF-1.4 fake-content"

        expected_resume = _make_resume()
        mock_create.return_value = expected_resume

        result = ResumeService.upload_resume(
            db=db,
            user_id=42,
            filename="my_cv.pdf",
            content_type="application/pdf",
            file_data=file_data,
            storage=storage,
        )

        # File was saved to storage
        storage.save.assert_called_once()
        saved_path: str = storage.save.call_args[0][1]
        assert saved_path.startswith("resumes/42/")
        assert saved_path.endswith(".pdf")

        # Repository was called to persist the record
        mock_create.assert_called_once_with(db, mock_create.call_args[0][1])

        # Returned object is the resume
        assert result is expected_resume

    @patch("app.services.resume_service.ResumeRepository.create")
    def test_upload_docx_succeeds(self, mock_create: MagicMock) -> None:
        """A valid DOCX upload is accepted."""
        db = _mock_db()
        storage = _mock_storage()
        docx_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        expected_resume = _make_resume()
        expected_resume.mime_type = docx_mime
        expected_resume.file_extension = ".docx"
        mock_create.return_value = expected_resume

        result = ResumeService.upload_resume(
            db=db,
            user_id=42,
            filename="resume.docx",
            content_type=docx_mime,
            file_data=b"PK fake docx content",
            storage=storage,
        )

        storage.save.assert_called_once()
        saved_path: str = storage.save.call_args[0][1]
        assert saved_path.endswith(".docx")
        assert result is expected_resume

    @patch("app.services.resume_service.ResumeRepository.create")
    def test_resume_record_has_correct_fields(self, mock_create: MagicMock) -> None:
        """The Resume ORM object passed to create() has the correct field values."""
        db = _mock_db()
        storage = _mock_storage()

        captured_resume: Resume | None = None

        def capture(db_arg, resume_arg):
            nonlocal captured_resume
            captured_resume = resume_arg
            return resume_arg

        mock_create.side_effect = capture

        ResumeService.upload_resume(
            db=db,
            user_id=7,
            filename="cv.pdf",
            content_type="application/pdf",
            file_data=b"x" * 512,
            storage=storage,
        )

        assert captured_resume is not None
        assert captured_resume.user_id == 7
        assert captured_resume.original_filename == "cv.pdf"
        assert captured_resume.mime_type == "application/pdf"
        assert captured_resume.file_extension == ".pdf"
        assert captured_resume.file_size_bytes == 512
        assert captured_resume.upload_status == UploadStatus.COMPLETED
        assert captured_resume.parsing_status == ParsingStatus.PENDING
        assert captured_resume.storage_provider == StorageProvider.LOCAL
        assert captured_resume.storage_path.startswith("resumes/7/")
        assert captured_resume.storage_path.endswith(".pdf")


# ---------------------------------------------------------------------------
# upload_resume — validation failures
# ---------------------------------------------------------------------------

class TestUploadResumeValidation:

    def test_invalid_mime_type_raises_invalid_file_type(self) -> None:
        """Unsupported MIME type raises InvalidFileTypeError."""
        with pytest.raises(InvalidFileTypeError):
            ResumeService.upload_resume(
                db=_mock_db(),
                user_id=1,
                filename="evil.exe",
                content_type="application/octet-stream",
                file_data=b"MZ evil",
                storage=_mock_storage(),
            )

    def test_text_plain_raises_invalid_file_type(self) -> None:
        """text/plain is not accepted even though it is readable."""
        with pytest.raises(InvalidFileTypeError):
            ResumeService.upload_resume(
                db=_mock_db(),
                user_id=1,
                filename="resume.txt",
                content_type="text/plain",
                file_data=b"some text",
                storage=_mock_storage(),
            )

    def test_empty_content_type_raises_invalid_file_type(self) -> None:
        """None or empty content_type raises InvalidFileTypeError."""
        with pytest.raises(InvalidFileTypeError):
            ResumeService.upload_resume(
                db=_mock_db(),
                user_id=1,
                filename="resume.pdf",
                content_type=None,
                file_data=b"%PDF content",
                storage=_mock_storage(),
            )

    @patch("app.services.resume_service.settings")
    def test_file_too_large_raises_file_too_large_error(
        self, mock_settings: MagicMock,
    ) -> None:
        """File exceeding the configured limit raises FileTooLargeError."""
        mock_settings.MAX_RESUME_SIZE_MB = 1
        mock_settings.STORAGE_BACKEND = "local"

        with pytest.raises(FileTooLargeError):
            ResumeService.upload_resume(
                db=_mock_db(),
                user_id=1,
                filename="huge.pdf",
                content_type="application/pdf",
                file_data=b"x" * (2 * 1024 * 1024),  # 2 MB
                storage=_mock_storage(),
            )

    def test_empty_file_raises_invalid_file_type(self) -> None:
        """Zero-byte upload raises InvalidFileTypeError (not FileTooLargeError)."""
        with pytest.raises(InvalidFileTypeError):
            ResumeService.upload_resume(
                db=_mock_db(),
                user_id=1,
                filename="empty.pdf",
                content_type="application/pdf",
                file_data=b"",
                storage=_mock_storage(),
            )

    def test_storage_failure_raises_resume_upload_error(self) -> None:
        """OSError from storage backend raises ResumeUploadError."""
        storage = _mock_storage()
        storage.save.side_effect = OSError("disk full")

        with pytest.raises(ResumeUploadError):
            ResumeService.upload_resume(
                db=_mock_db(),
                user_id=1,
                filename="cv.pdf",
                content_type="application/pdf",
                file_data=b"content",
                storage=storage,
            )


# ---------------------------------------------------------------------------
# get_resume — ownership enforcement
# ---------------------------------------------------------------------------

class TestGetResume:

    @patch("app.services.resume_service.ResumeRepository.get_by_id_and_user")
    def test_get_resume_returns_owned_resume(self, mock_get: MagicMock) -> None:
        """get_resume returns the resume when it belongs to the requesting user."""
        resume = _make_resume(id=5, user_id=10)
        mock_get.return_value = resume

        result = ResumeService.get_resume(db=_mock_db(), resume_id=5, user_id=10)

        assert result is resume
        mock_get.assert_called_once()

    @patch("app.services.resume_service.ResumeRepository.get_by_id_and_user")
    def test_get_resume_raises_not_found_for_wrong_user(
        self, mock_get: MagicMock
    ) -> None:
        """get_resume raises ResumeNotFoundError when the user doesn't own the resume."""
        mock_get.return_value = None

        with pytest.raises(ResumeNotFoundError):
            ResumeService.get_resume(db=_mock_db(), resume_id=5, user_id=99)

    @patch("app.services.resume_service.ResumeRepository.get_by_id_and_user")
    def test_get_resume_raises_not_found_for_nonexistent(
        self, mock_get: MagicMock
    ) -> None:
        """get_resume raises ResumeNotFoundError when the record does not exist."""
        mock_get.return_value = None

        with pytest.raises(ResumeNotFoundError):
            ResumeService.get_resume(db=_mock_db(), resume_id=9999, user_id=1)


# ---------------------------------------------------------------------------
# get_user_resumes
# ---------------------------------------------------------------------------

class TestGetUserResumes:

    @patch("app.services.resume_service.ResumeRepository.get_by_user")
    def test_list_returns_all_user_resumes(self, mock_get: MagicMock) -> None:
        """get_user_resumes returns the list from the repository."""
        resumes = [_make_resume(id=1), _make_resume(id=2)]
        mock_get.return_value = resumes

        result = ResumeService.get_user_resumes(db=_mock_db(), user_id=42)

        assert result == resumes
        mock_get.assert_called_once()

    @patch("app.services.resume_service.ResumeRepository.get_by_user")
    def test_list_returns_empty_for_new_user(self, mock_get: MagicMock) -> None:
        """get_user_resumes returns an empty list when the user has no resumes."""
        mock_get.return_value = []

        result = ResumeService.get_user_resumes(db=_mock_db(), user_id=99)

        assert result == []


# ---------------------------------------------------------------------------
# delete_resume — file and metadata removal
# ---------------------------------------------------------------------------

class TestDeleteResume:

    @patch("app.services.resume_service.ResumeRepository.delete")
    @patch("app.services.resume_service.ResumeRepository.get_by_id_and_user")
    def test_delete_removes_file_and_record(
        self,
        mock_get: MagicMock,
        mock_delete: MagicMock,
    ) -> None:
        """delete_resume removes the file from storage and the record from DB."""
        resume = _make_resume(id=3, storage_path="resumes/42/abc.pdf")
        mock_get.return_value = resume
        storage = _mock_storage()

        ResumeService.delete_resume(
            db=_mock_db(),
            resume_id=3,
            user_id=42,
            storage=storage,
        )

        storage.delete.assert_called_once_with("resumes/42/abc.pdf")
        mock_delete.assert_called_once()

    @patch("app.services.resume_service.ResumeRepository.delete")
    @patch("app.services.resume_service.ResumeRepository.get_by_id_and_user")
    def test_delete_still_removes_record_on_storage_failure(
        self,
        mock_get: MagicMock,
        mock_delete: MagicMock,
    ) -> None:
        """DB record is deleted even if the storage delete fails (graceful degradation)."""
        resume = _make_resume(id=4, storage_path="resumes/42/xyz.pdf")
        mock_get.return_value = resume

        storage = _mock_storage()
        storage.delete.side_effect = OSError("File not found on disk")

        # Should NOT raise
        ResumeService.delete_resume(
            db=_mock_db(),
            resume_id=4,
            user_id=42,
            storage=storage,
        )

        mock_delete.assert_called_once()

    @patch("app.services.resume_service.ResumeRepository.get_by_id_and_user")
    def test_delete_raises_not_found_for_wrong_user(
        self, mock_get: MagicMock
    ) -> None:
        """delete_resume raises ResumeNotFoundError when user doesn't own the resume."""
        mock_get.return_value = None

        with pytest.raises(ResumeNotFoundError):
            ResumeService.delete_resume(
                db=_mock_db(),
                resume_id=1,
                user_id=999,
                storage=_mock_storage(),
            )


# ---------------------------------------------------------------------------
# Accepted MIME types constant sanity check
# ---------------------------------------------------------------------------

class TestAcceptedMimeTypes:

    def test_pdf_is_accepted(self) -> None:
        assert "application/pdf" in ACCEPTED_MIME_TYPES

    def test_docx_is_accepted(self) -> None:
        assert (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            in ACCEPTED_MIME_TYPES
        )

    def test_pdf_extension(self) -> None:
        assert ACCEPTED_MIME_TYPES["application/pdf"] == ".pdf"

    def test_docx_extension(self) -> None:
        assert ACCEPTED_MIME_TYPES[
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ] == ".docx"
