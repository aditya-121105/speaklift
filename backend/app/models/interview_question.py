from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
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
    QuestionType,
    QuestionCategory,
)


class InterviewQuestion(
    Base,
    TimestampMixin,
):
    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    interview_session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "interview_sessions.id"
        ),
        nullable=False,
    )

    parent_question_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "interview_questions.id"
        ),
        nullable=True,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType),
        nullable=False,
    )

    question_category: Mapped[
        QuestionCategory
    ] = mapped_column(
        Enum(QuestionCategory),
        nullable=False,
    )

    question_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_asked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )