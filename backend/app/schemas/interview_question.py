from datetime import datetime

from pydantic import BaseModel

from app.shared.enums import (
    QuestionCategory,
    QuestionType,
)


class InterviewQuestionResponse(
    BaseModel
):
    id: int

    question_text: str

    question_type: QuestionType

    question_category: QuestionCategory

    question_order: int

    is_asked: bool

    created_at: datetime

class SubmitAnswerResponse(
    BaseModel
):
    interview_completed: bool

    next_question: (
        InterviewQuestionResponse
        | None
    ) = None