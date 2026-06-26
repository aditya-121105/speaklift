#app/models/interview_evaluation.py

from sqlalchemy import (
    ForeignKey,
    Integer,
    Enum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import (
    Base,
    TimestampMixin,
)
from app.shared.enums import (
    EvaluationSource,
)



class InterviewEvaluation(
    Base,
    TimestampMixin,
):
    __tablename__ = "interview_evaluations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    interview_session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "interview_sessions.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )
# Scores
    technical_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    communication_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    behavioral_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    confidence_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    overall_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

# AI feedback
    strengths: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
    )

    weaknesses: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
    )

    recommendations: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
    )
# metadata
    evaluation_source: Mapped[
        EvaluationSource
    ] = mapped_column(
        Enum(EvaluationSource),
        nullable=False,
    )

