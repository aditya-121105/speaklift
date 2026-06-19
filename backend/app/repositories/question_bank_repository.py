from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.question_bank import QuestionBank
from app.shared.enums import (
    ExperienceLevel,
    QuestionCategory,
)


class QuestionBankRepository:

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
                QuestionBank.experience_level
                == experience_level,
                QuestionBank.is_active.is_(True),
            )
        )

        if category:
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
    def increment_usage_count(
        db: Session,
        question: QuestionBank,
    ) -> None:

        question.usage_count += 1

        db.commit()

        db.refresh(question)