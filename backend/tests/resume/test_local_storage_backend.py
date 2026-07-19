"""
tests/resume/test_local_storage_backend.py

Unit tests for LocalStorageBackend.

Tests use tmp_path (pytest built-in) so no real project directories are touched.
"""

from pathlib import Path

from app.core.storage import LocalStorageBackend


class TestLocalStorageBackendSave:

    def test_save_creates_file(self, tmp_path: Path) -> None:
        """save() writes the file at the expected location."""
        backend = LocalStorageBackend(root_dir=tmp_path)
        data = b"hello resume"
        path = "resumes/1/abc.pdf"

        returned_path = backend.save(data, path)

        assert returned_path == path
        full = tmp_path / path
        assert full.exists()
        assert full.read_bytes() == data

    def test_save_creates_intermediate_directories(self, tmp_path: Path) -> None:
        """save() creates parent directories that do not yet exist."""
        backend = LocalStorageBackend(root_dir=tmp_path)

        backend.save(b"data", "deep/nested/dir/file.pdf")

        assert (tmp_path / "deep" / "nested" / "dir" / "file.pdf").exists()

    def test_save_overwrites_existing_file(self, tmp_path: Path) -> None:
        """save() overwrites an existing file at the same path."""
        backend = LocalStorageBackend(root_dir=tmp_path)
        path = "resume.pdf"

        backend.save(b"original", path)
        backend.save(b"updated", path)

        assert (tmp_path / path).read_bytes() == b"updated"


class TestLocalStorageBackendDelete:

    def test_delete_removes_existing_file(self, tmp_path: Path) -> None:
        """delete() removes a file that exists."""
        backend = LocalStorageBackend(root_dir=tmp_path)
        path = "resume.pdf"
        backend.save(b"content", path)

        backend.delete(path)

        assert not (tmp_path / path).exists()

    def test_delete_is_idempotent(self, tmp_path: Path) -> None:
        """delete() does not raise when the file does not exist."""
        backend = LocalStorageBackend(root_dir=tmp_path)

        # Should not raise
        backend.delete("nonexistent/file.pdf")

    def test_delete_does_not_affect_other_files(self, tmp_path: Path) -> None:
        """delete() only removes the specified file, not siblings."""
        backend = LocalStorageBackend(root_dir=tmp_path)
        backend.save(b"a", "resumes/a.pdf")
        backend.save(b"b", "resumes/b.pdf")

        backend.delete("resumes/a.pdf")

        assert not (tmp_path / "resumes" / "a.pdf").exists()
        assert (tmp_path / "resumes" / "b.pdf").exists()


class TestLocalStorageBackendGetAbsolutePath:

    def test_returns_absolute_path(self, tmp_path: Path) -> None:
        """get_absolute_path() returns the full filesystem path."""
        backend = LocalStorageBackend(root_dir=tmp_path)
        result = backend.get_absolute_path("resumes/1/file.pdf")

        assert result == tmp_path / "resumes" / "1" / "file.pdf"
        assert result.is_absolute()


class TestLocalStorageBackendInit:

    def test_creates_root_dir_if_not_exists(self, tmp_path: Path) -> None:
        """LocalStorageBackend creates the root directory on init if missing."""
        new_dir = tmp_path / "created_by_backend"
        assert not new_dir.exists()

        LocalStorageBackend(root_dir=new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()
