# app/models/interview_session.py

from datetime import datetime

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base, TimestampMixin
from app.shared.enums import (
    ExperienceLevel,
    InterviewStatus,
)


class InterviewSession(Base, TimestampMixin):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel),
        nullable=False,
    )

    duration_minutes: Mapped[int] = mapped_column(
        nullable=False,
    )

    resume_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    job_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[InterviewStatus] = mapped_column(
        Enum(InterviewStatus),
        nullable=False,
        default=InterviewStatus.CREATED,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )