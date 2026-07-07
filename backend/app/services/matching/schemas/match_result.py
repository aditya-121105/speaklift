from pydantic import BaseModel, ConfigDict
from .skill_match_result import SkillMatchResult
from .experience_match_result import ExperienceMatchResult
from .education_match_result import EducationMatchResult
from .match_statistics import MatchStatistics

class MatchResult(BaseModel):
    """
    Immutable business aggregate containing the overall deterministic results
    of all matching operations.
    """
    model_config = ConfigDict(frozen=True)

    skill_result: SkillMatchResult
    experience_result: ExperienceMatchResult
    education_result: EducationMatchResult
    statistics: MatchStatistics
    score: float
