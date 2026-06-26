from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.shared.enums import (
    EvaluationSource,
)


class InterviewEvaluationResponse(
    BaseModel,
):
    id: int

    interview_session_id: int

    technical_score: int

    communication_score: int

    behavioral_score: int

    confidence_score: int

    overall_score: int

    strengths: list[str]

    weaknesses: list[str]

    recommendations: list[str]

    evaluation_source: EvaluationSource

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class EvaluateInterviewResponse(
    BaseModel,
):
    evaluation: InterviewEvaluationResponse