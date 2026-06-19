from sqlalchemy.orm import Session

from app.models.interview_question import (
    InterviewQuestion,
)
from app.models.interview_session import (
    InterviewSession,
)

from app.repositories.question_bank_repository import (
    QuestionBankRepository,
)

from app.shared.enums import (
    QuestionCategory,
)


class InterviewQuestionGeneratorService:

    @staticmethod
    def generate_questions(
        db: Session,
        interview_session: InterviewSession,
    ) -> list[InterviewQuestion]:

        distribution = (
            InterviewQuestionGeneratorService
            .get_question_distribution(
                interview_session.duration_minutes
            )
        )

        generated_questions: list[
            InterviewQuestion
        ] = []

        for (
            category,
            count,
        ) in distribution.items():

            questions = (
                QuestionBankRepository.get_questions(
                    db=db,
                    role=interview_session.role,
                    experience_level=(
                        interview_session
                        .experience_level
                    ),
                    category=category,
                    limit=count,
                )
            )

            print(
                f"{category.value}: "
                f"{len(questions)} questions found"
            )

        return generated_questions

    @staticmethod
    def get_question_distribution(
        duration_minutes: int,
    ) -> dict[QuestionCategory, int]:

        if duration_minutes <= 15:
            return {
                QuestionCategory.INTRODUCTION: 1,
                QuestionCategory.PROJECT: 2,
                QuestionCategory.TECHNICAL: 3,
                QuestionCategory.BEHAVIORAL: 1,
                QuestionCategory.ROLE_SPECIFIC: 1,
            }

        if duration_minutes <= 30:
            return {
                QuestionCategory.INTRODUCTION: 2,
                QuestionCategory.PROJECT: 3,
                QuestionCategory.TECHNICAL: 5,
                QuestionCategory.BEHAVIORAL: 3,
                QuestionCategory.ROLE_SPECIFIC: 2,
            }

        return {
            QuestionCategory.INTRODUCTION: 3,
            QuestionCategory.PROJECT: 4,
            QuestionCategory.TECHNICAL: 8,
            QuestionCategory.BEHAVIORAL: 4,
            QuestionCategory.ROLE_SPECIFIC: 3,
        }