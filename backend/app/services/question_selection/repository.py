from typing import Protocol
from sqlalchemy.orm import Session
from app.models.question_bank import QuestionBank
from app.services.interview_planner.schemas.interview_objective import InterviewObjective
from app.shared.enums import ExperienceLevel, QuestionCategory

class QuestionRepository(Protocol):
    def find_best_questions(
        self,
        db: Session,
        role: str,
        experience_level: ExperienceLevel,
        objective: InterviewObjective,
        limit: int = 5,
    ) -> list[QuestionBank]:
        ...

    def get_questions(
        self,
        db: Session,
        role: str,
        experience_level: ExperienceLevel,
        category: QuestionCategory | None = None,
        limit: int = 10,
    ) -> list[QuestionBank]:
        ...
