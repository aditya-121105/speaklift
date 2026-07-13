from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation

class QualitativeRating(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"

class EvaluationObservation(BaseModel):
    model_config = ConfigDict(frozen=True)
    category: str = Field(description="Broad category of the observation.")
    observation: str = Field(description="The specific qualitative finding.")
    evidence: str | None = Field(default=None, description="Optional quote or evidence from the answer.")
class ImprovementSuggestion(BaseModel):
    model_config = ConfigDict(frozen=True)
    category: str = Field(description="Category of the suggestion (e.g., Tone, Clarity, Conciseness).")
    description: str = Field(description="Actionable advice on how to improve.")
    example: str | None = Field(default=None, description="Optional example demonstrating the improvement.")

class CommunicationFeedback(BaseModel):
    model_config = ConfigDict(frozen=True)
    clarity_rating: QualitativeRating = Field(description="Qualitative assessment of how clear the answer was.")
    confidence_rating: QualitativeRating = Field(description="Qualitative assessment of the candidate's confidence.")
    tone: str = Field(description="Narrative description of the candidate's tone.")
    feedback: str = Field(description="Detailed narrative feedback on communication skills.")

class AIEvaluationResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    strengths: list[EvaluationObservation] = Field(default_factory=list, description="Key strengths identified in the answer.")
    weaknesses: list[EvaluationObservation] = Field(default_factory=list, description="Areas where the answer fell short.")
    communication: CommunicationFeedback = Field(description="Qualitative feedback on communication style.")
    suggestions: list[ImprovementSuggestion] = Field(default_factory=list, description="Actionable improvement tips.")

class EnhancedAnswerEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True)
    deterministic_metrics: AnswerEvaluation = Field(description="Objective measurements (keyword/concept coverage).")
    ai_interpretation: AIEvaluationResult | None = Field(default=None, description="Subjective, qualitative assessment from the LLM.")
