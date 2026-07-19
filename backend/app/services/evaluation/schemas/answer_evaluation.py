from pydantic import BaseModel, ConfigDict, Field
from app.services.evaluation.schemas.grammar_evaluation import GrammarEvaluation
from app.services.evaluation.schemas.readability_evaluation import ReadabilityEvaluation
from app.services.evaluation.schemas.confidence_evaluation import ConfidenceEvaluation
from app.services.evaluation.schemas.semantic_evaluation import SemanticEvaluation


class AnswerEvaluation(BaseModel):
    """
    Complete deterministic evaluation result for one candidate answer.

    Fields
    ------
    keyword_coverage      : Fraction of question content words present in answer.
    concept_coverage      : Fraction of question named-entities present in answer.
    completeness          : Token-length heuristic normalised to [0, 1].
    vocabulary_statistics : Dict from VocabularyFeatureExtractor.
    overall_score         : Weighted composite of coverage and completeness.
    grammar               : Grammar quality metrics (optional – requires full NLP).
    readability           : Standard readability metrics (optional).
    confidence            : Filler-word / hedging confidence indicators (optional).
    semantic_similarity   : Embedding cosine relevance score (optional).
    """

    model_config = ConfigDict(frozen=True)

    keyword_coverage: float = Field(ge=0.0, le=1.0)
    concept_coverage: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    vocabulary_statistics: dict[str, float | int] = Field(default_factory=dict)
    overall_score: float = Field(ge=0.0, le=1.0)

    # Optional extended metrics added in M2.1
    grammar: GrammarEvaluation | None = Field(default=None)
    readability: ReadabilityEvaluation | None = Field(default=None)
    confidence: ConfidenceEvaluation | None = Field(default=None)
    semantic_similarity: SemanticEvaluation | None = Field(default=None)
