#backend/app/models/question_bank.py
from sqlalchemy import (
    Boolean,
    Enum,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import (
    Base,
    TimestampMixin,
)

from app.shared.enums import (
    DifficultyLevel,
    ExperienceLevel,
    QuestionCategory,
    QuestionSource,
)


class QuestionBank(
    Base,
    TimestampMixin,
):
    """
    Central AI-ready knowledge base for interview questions.

    Every question contains metadata that allows the Interview Engine
    to retrieve the most appropriate question based on interview
    objectives.

    Future versions will also support semantic search using embeddings.
    """

    __tablename__ = "question_bank"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    role: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    experience_level: Mapped[
        ExperienceLevel
    ] = mapped_column(
        Enum(
            ExperienceLevel,
            name="experiencelevel",
            create_type=False,
        ),
        nullable=False,
    )

    category: Mapped[
        QuestionCategory
    ] = mapped_column(
        Enum(
            QuestionCategory,
            name="questioncategory",
            create_type=False,
        ),
        nullable=False,
    )

    difficulty: Mapped[
        DifficultyLevel
    ] = mapped_column(
        Enum(DifficultyLevel),
        nullable=False,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # ==========================================================
    # AI Metadata
    # ==========================================================

    skills: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    technologies: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    expected_concepts: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    has_follow_up: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    # ==========================================================
    # Metadata
    # ==========================================================

    source: Mapped[
        QuestionSource
    ] = mapped_column(
        Enum(QuestionSource),
        nullable=False,
    )

    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )