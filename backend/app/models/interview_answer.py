# app/models/interview_answer.py
from sqlalchemy import (
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
    AnswerSource,
)


class InterviewAnswer(
    Base,
    TimestampMixin,
):
    __tablename__ = "interview_answers"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    interview_session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "interview_sessions.id"
        ),
        nullable=False,
    )

    interview_question_id: Mapped[int] = mapped_column(
        ForeignKey(
            "interview_questions.id"
        ),
        nullable=False,
    )

    transcript: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer_source: Mapped[
        AnswerSource
    ] = mapped_column(
        Enum(AnswerSource),
        nullable=False,
    )

    answer_duration_seconds: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )