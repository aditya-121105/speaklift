# backend/app/core/storage.py
"""
Provider-agnostic file storage abstraction.

Design
------
StorageBackend is an abstract base class. Every concrete implementation must
implement save(), delete(), and get_absolute_path().

When the project migrates to S3, only S3StorageBackend needs to be added.
No service or endpoint code changes.

Current implementations
-----------------------
LocalStorageBackend — stores files on the local filesystem under STORAGE_LOCAL_ROOT.

Future implementations (not implemented in this sprint)
-----------------------
S3StorageBackend — stores files in AWS S3.

Usage
-----
Inject StorageBackend via app.dependencies.storage.get_storage.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract interface for all file storage providers."""

    @abstractmethod
    def save(self, file_data: bytes, storage_path: str) -> str:
        """
        Persist file_data at the given logical storage_path.

        Parameters
        ----------
        file_data:    raw file bytes
        storage_path: provider-agnostic logical path
                      e.g. "resumes/42/abc123.pdf"
                      For local storage this is relative to STORAGE_LOCAL_ROOT.
                      For S3 this is the object key.

        Returns
        -------
        The storage_path as stored — callers must persist this value so they
        can retrieve or delete the file later.
        """

    @abstractmethod
    def delete(self, storage_path: str) -> None:
        """
        Remove the file at storage_path.

        Implementations must be idempotent — deleting a non-existent path
        should not raise an error.
        """

    @abstractmethod
    def get_absolute_path(self, storage_path: str) -> Path:
        """
        Return the fully-resolved filesystem path for the given storage_path.

        Used by endpoints to serve files via FileResponse.

        Note: S3StorageBackend will not support this method meaningfully — it
        will return presigned URLs instead. The endpoint layer must be aware of
        this distinction when S3 is introduced.
        """


class LocalStorageBackend(StorageBackend):
    """
    Stores files on the local filesystem.

    All paths are relative to root_dir. The directory is created on init if it
    does not already exist.
    """

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir.resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "LocalStorageBackend initialised. Root: %s",
            self.root_dir,
        )

    def save(self, file_data: bytes, storage_path: str) -> str:
        full_path = self.root_dir / storage_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            full_path.write_bytes(file_data)
        except OSError as exc:
            logger.error(
                "Failed to write file to %s: %s",
                full_path,
                exc,
            )
            raise

        logger.debug("Saved %d bytes → %s", len(file_data), full_path)
        return storage_path

    def delete(self, storage_path: str) -> None:
        full_path = self.root_dir / storage_path
        if full_path.exists():
            full_path.unlink()
            logger.debug("Deleted %s", full_path)
        else:
            logger.warning(
                "delete() called for non-existent path: %s",
                full_path,
            )

    def get_absolute_path(self, storage_path: str) -> Path:
        return self.root_dir / storage_path
