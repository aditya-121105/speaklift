from pydantic import BaseModel, ConfigDict

class MatchStatistics(BaseModel):
    """
    Immutable, domain-agnostic factual statistics for a match.
    """
    model_config = ConfigDict(frozen=True)
    
    total_required: int
    matched_required: int
    
    total_preferred: int
    matched_preferred: int
    
    total_optional: int
    matched_optional: int
    
    total_unknown: int
    matched_unknown: int
    
    total_candidate_items: int
    extra_candidate_items: int
