from pydantic import BaseModel, ConfigDict
from app.services.candidate_profile.schemas.technology import TechNode
from .match_statistics import MatchStatistics

class SkillMatchResult(BaseModel):
    """
    Immutable result of a skill match operation.
    """
    model_config = ConfigDict(frozen=True)
    
    matched_required: list[TechNode]
    missing_required: list[TechNode]
    
    matched_preferred: list[TechNode]
    missing_preferred: list[TechNode]
    
    matched_optional: list[TechNode]
    missing_optional: list[TechNode]
    
    matched_unknown: list[TechNode]
    missing_unknown: list[TechNode]
    
    extra_candidate_technologies: list[TechNode]
    
    statistics: MatchStatistics
    score: float
