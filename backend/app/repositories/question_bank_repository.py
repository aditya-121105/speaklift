from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.question_bank import QuestionBank
from app.services.interview_planner.schemas.interview_objective import (
    InterviewObjective,
)
from app.shared.enums import (
    ExperienceLevel,
    QuestionCategory,
)


from app.services.question_selection.repository import QuestionRepository

class QuestionBankRepository(QuestionRepository):

    @staticmethod
    def create(
        db: Session,
        question: QuestionBank,
    ) -> QuestionBank:

        try:
            db.add(question)
            db.commit()
            db.refresh(question)
            return question

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_by_id(
        db: Session,
        question_id: int,
    ) -> QuestionBank | None:

        return (
            db.query(QuestionBank)
            .filter(
                QuestionBank.id == question_id
            )
            .first()
        )

    @staticmethod
    def get_questions(
        db: Session,
        role: str,
        experience_level: ExperienceLevel,
        category: QuestionCategory | None = None,
        limit: int = 10,
    ) -> list[QuestionBank]:

        query = (
            db.query(QuestionBank)
            .filter(
                QuestionBank.role == role,
                QuestionBank.experience_level == experience_level,
                QuestionBank.is_active.is_(True),
            )
        )

        if category is not None:
            query = query.filter(
                QuestionBank.category == category
            )

        return (
            query.order_by(
                QuestionBank.usage_count.asc(),
                func.random(),
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def find_best_questions(
        db: Session,
        role: str,
        experience_level: ExperienceLevel,
        objective: InterviewObjective,
        limit: int = 5,
    ) -> list[QuestionBank]:
        """
        Return the most relevant questions for a given interview objective.

        Current Strategy (v1)

        1. Match objective against skills.
        2. Match objective against technologies.
        3. Least-used questions first.
        4. Randomize equally-used questions.

        Future Strategy (v2)

        Replace metadata matching with vector similarity search.
        """

        return (
            db.query(QuestionBank)
            .filter(
                QuestionBank.role == role,
                QuestionBank.experience_level == experience_level,
                QuestionBank.is_active.is_(True),
                or_(
                    QuestionBank.skills.contains(
                        [objective.name]
                    ),
                    QuestionBank.technologies.contains(
                        [objective.name]
                    ),
                ),
            )
            .order_by(
                QuestionBank.usage_count.asc(),
                func.random(),
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def increment_usage_count(
        db: Session,
        question: QuestionBank,
    ) -> None:

        question.usage_count += 1

        db.commit()

        db.refresh(question)