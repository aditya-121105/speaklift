from pydantic import BaseModel, ConfigDict
from .match_statistics import MatchStatistics

class ExperienceMatchResult(BaseModel):
    """
    Immutable business aggregate containing the deterministic results
    of an experience matching operation.
    """
    model_config = ConfigDict(frozen=True)

    candidate_months: int
    required_minimum_months: int | None
    required_maximum_months: int | None
    is_satisfied: bool
    deficit_months: int
    surplus_months: int
    statistics: MatchStatistics
    score: float
