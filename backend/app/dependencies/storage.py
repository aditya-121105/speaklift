# backend/app/dependencies/storage.py
"""
FastAPI dependency provider for the storage backend.

Pattern: module-level singleton, lazily initialised on first call.
Mirrors the NLPResourceManager pattern already in use for spaCy.

To switch to S3:
  1. Set STORAGE_BACKEND=s3 in .env
  2. Implement S3StorageBackend in app/core/storage.py
  3. Add the elif branch here
  No service or endpoint code changes needed.
"""

from functools import lru_cache
from pathlib import Path

from app.core.config import settings
from app.core.storage import LocalStorageBackend, StorageBackend


@lru_cache(maxsize=1)
def get_storage() -> StorageBackend:
    """
    Return the configured storage backend singleton.

    lru_cache(maxsize=1) ensures a single instance is created regardless of
    how many requests arrive concurrently.
    """
    if settings.STORAGE_BACKEND == "local":
        return LocalStorageBackend(
            root_dir=Path(settings.STORAGE_LOCAL_ROOT),
        )

    raise NotImplementedError(
        f"Storage backend '{settings.STORAGE_BACKEND}' is not implemented. "
        "Set STORAGE_BACKEND=local in .env."
    )
