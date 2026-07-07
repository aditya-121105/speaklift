from pydantic import BaseModel, ConfigDict
from .match_statistics import MatchStatistics

class EducationMatchResult(BaseModel):
    """
    Immutable business aggregate containing the deterministic results
    of an education matching operation.
    """
    model_config = ConfigDict(frozen=True)

    highest_qualification: str | None
    required_qualification: str | None
    qualification_satisfied: bool
    matched_degrees: list[str]
    missing_degrees: list[str]
    statistics: MatchStatistics
    score: float
