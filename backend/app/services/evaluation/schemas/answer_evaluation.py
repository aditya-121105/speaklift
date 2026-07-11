from pydantic import BaseModel, ConfigDict

class AnswerEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    keyword_coverage: float
    concept_coverage: float
    completeness: float
    vocabulary_statistics: dict[str, float | int]
    overall_score: float
