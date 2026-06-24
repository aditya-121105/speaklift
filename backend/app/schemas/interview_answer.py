from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.shared.enums import (
    AnswerSource,
)


class SubmitAnswerRequest(BaseModel):
    question_id: int

    transcript: str

    answer_source: AnswerSource

    answer_duration_seconds: int | None = None


class InterviewAnswerResponse(
    BaseModel
):
    id: int

    interview_session_id: int

    interview_question_id: int

    transcript: str

    answer_source: AnswerSource

    answer_duration_seconds: int | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )