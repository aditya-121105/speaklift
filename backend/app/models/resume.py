# backend/app/models/resume.py
"""
Resume ORM model.

Stores file metadata only. No extracted AI information lives here.
Parsed content (skills, experience, education) belongs to the Profile model,
which will be enriched by the NLP pipeline in Sprint C.2.

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

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.shared.enums import ParsingStatus, StorageProvider, UploadStatus


class Resume(Base, TimestampMixin):
    """
    Represents one uploaded resume file.

    Lifecycle
    ---------
    upload_status: PENDING → COMPLETED | FAILED

    parsing_status tracks the NLP pipeline state (Sprint C.2):
    PENDING → PROCESSING → COMPLETED | FAILED | SKIPPED

    TimestampMixin provides:
      created_at  — used as the canonical "uploaded_at" timestamp
      updated_at  — last modification timestamp
    """

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # File identity
    # ------------------------------------------------------------------

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Filename as provided by the user at upload time.",
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="UUID-based filename used on the storage layer.",
    )

    file_extension: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Canonical file extension, e.g. '.pdf' or '.docx'.",
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME type of the uploaded file (e.g. application/pdf).",
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="File size in bytes.",
    )

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    storage_provider: Mapped[StorageProvider] = mapped_column(
        Enum(
            StorageProvider,
            name="storageprovider",
        ),
        nullable=False,
        default=StorageProvider.LOCAL,
        server_default="LOCAL",
        comment="Which storage backend holds this file.",
    )

    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment=(
            "Provider-agnostic logical path used by StorageBackend. "
            "For local storage: relative path from STORAGE_LOCAL_ROOT. "
            "For S3: object key."
        ),
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    upload_status: Mapped[UploadStatus] = mapped_column(
        Enum(
            UploadStatus,
            name="uploadstatus",
        ),
        nullable=False,
        default=UploadStatus.PENDING,
        server_default="PENDING",
    )

    parsing_status: Mapped[ParsingStatus] = mapped_column(
        Enum(
            ParsingStatus,
            name="parsingstatus",
        ),
        nullable=False,
        default=ParsingStatus.PENDING,
        server_default="PENDING",
    )

    # ------------------------------------------------------------------
    # Timestamps
    # TimestampMixin provides created_at (== uploaded_at) and updated_at.
    # parsed_at is set by the NLP pipeline when parsing completes.
    # ------------------------------------------------------------------

    parsed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
