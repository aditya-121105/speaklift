from sqlalchemy import ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

class AnswerEvaluation(Base, TimestampMixin):
    """
    Persistence model for granular answer-level evaluation results.
    Captures both deterministic metrics (NLP) and AI-generated insights.
    """
    __tablename__ = "answer_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    interview_answer_id: Mapped[int] = mapped_column(
        ForeignKey("interview_answers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Deterministic Metrics (Indexed / Queryable Columns)
    # ---------------------------------------------------------
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    keyword_coverage: Mapped[float] = mapped_column(Float, nullable=False)
    concept_coverage: Mapped[float] = mapped_column(Float, nullable=False)
    completeness: Mapped[float] = mapped_column(Float, nullable=False)
    
    grammar_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    readability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    semantic_similarity: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ---------------------------------------------------------
    # Deterministic Details (JSONB for Schema Evolution Flexibility)
    # ---------------------------------------------------------
    vocabulary_statistics: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    grammar_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    readability_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    confidence_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    semantic_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ---------------------------------------------------------
    # AI Qualitative Evaluation
    # ---------------------------------------------------------
    strengths: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    weaknesses: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    
    communication_clarity: Mapped[str | None] = mapped_column(String, nullable=True)
    communication_confidence: Mapped[str | None] = mapped_column(String, nullable=True)
    communication_tone: Mapped[str | None] = mapped_column(String, nullable=True)
    communication_feedback: Mapped[str | None] = mapped_column(String, nullable=True)

    # ---------------------------------------------------------
    # Metadata & Versioning
    # ---------------------------------------------------------
    engine_version: Mapped[str] = mapped_column(String, nullable=False, default="1.0")
