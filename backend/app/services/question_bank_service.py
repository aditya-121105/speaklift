from sqlalchemy.orm import Session

from app.models.question_bank import QuestionBank
from app.repositories.question_bank_repository import (
    QuestionBankRepository,
)
from app.shared.enums import (
    ExperienceLevel,
    QuestionCategory,
    DifficultyLevel,
    QuestionSource,
)


class QuestionBankService:

    @staticmethod
    def create_question(
        db: Session,
        role: str,
        experience_level: ExperienceLevel,
        category: QuestionCategory,
        difficulty: DifficultyLevel,
        question_text: str,
        source: QuestionSource,
    ) -> QuestionBank:

        question = QuestionBank(
            role=role,
            experience_level=experience_level,
            category=category,
            difficulty=difficulty,
            question_text=question_text,
            source=source,
        )

        return (
            QuestionBankRepository.create(
                db,
                question,
            )
        )

    @staticmethod
    def get_questions(
        db: Session,
        role: str,
        experience_level: ExperienceLevel,
        category: QuestionCategory | None = None,
        limit: int = 10,
    ) -> list[QuestionBank]:

        return (
            QuestionBankRepository.get_questions(
                db=db,
                role=role,
                experience_level=experience_level,
                category=category,
                limit=limit,
            )
        )