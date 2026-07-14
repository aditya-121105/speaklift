# backend/app/models/job_description.py
"""
Job Description ORM model.

Stores file metadata only. No extracted AI information lives here.
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.shared.enums import ParsingStatus, StorageProvider, UploadStatus


class JobDescription(Base, TimestampMixin):
    """
    Represents one uploaded job description file.
    """

    __tablename__ = "job_descriptions"

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

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_extension: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    storage_provider: Mapped[StorageProvider] = mapped_column(
        Enum(
            StorageProvider,
            name="storageprovider",
            create_type=False,
        ),
        nullable=False,
        default=StorageProvider.LOCAL,
        server_default="LOCAL",
    )

    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    upload_status: Mapped[UploadStatus] = mapped_column(
        Enum(
            UploadStatus,
            name="uploadstatus",
            create_type=False,
        ),
        nullable=False,
        default=UploadStatus.PENDING,
        server_default="PENDING",
    )

    parsing_status: Mapped[ParsingStatus] = mapped_column(
        Enum(
            ParsingStatus,
            name="parsingstatus",
            create_type=False,
        ),
        nullable=False,
        default=ParsingStatus.PENDING,
        server_default="PENDING",
    )

    parsed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    job_profile_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Persisted JSON payload of the extracted JobProfile aggregate.",
    )
