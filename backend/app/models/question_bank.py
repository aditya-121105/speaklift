from sqlalchemy import (
    Enum,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Boolean,
    Enum,
    Integer,
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
    ExperienceLevel,
    QuestionCategory,
    DifficultyLevel,
    QuestionSource,
)


class QuestionBank(
    Base,
    TimestampMixin,
):
    __tablename__ = "question_bank"

    id: Mapped[int] = mapped_column(
        primary_key=True
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
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )