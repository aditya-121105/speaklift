from sqlalchemy.orm import Session

from app.models.interview_question import (
    InterviewQuestion,
)
from app.models.interview_session import (
    InterviewSession,
)

from app.repositories.interview_question_repository import (
    InterviewQuestionRepository,
)
from app.repositories.question_bank_repository import (
    QuestionBankRepository,
)

from app.shared.enums import (
    QuestionCategory,
    QuestionType,
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

        question_order = 1

        try:

            for (
                category,
                count,
            ) in distribution.items():

                bank_questions = (
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
                    f"{len(bank_questions)} questions found"
                )

                for bank_question in bank_questions:

                    # Update usage count
                    bank_question.usage_count += 1

                    interview_question = (
                        InterviewQuestion(
                            interview_session_id=(
                                interview_session.id
                            ),
                            question_text=(
                                bank_question.question_text
                            ),
                            question_type=(
                                QuestionType.PRIMARY
                            ),
                            question_category=category,
                            question_order=question_order,
                            is_asked=False,
                        )
                    )

                    generated_questions.append(
                        interview_question
                    )

                    question_order += 1

            if generated_questions:

                db.add_all(
                    generated_questions
                )

                db.commit()

                for question in generated_questions:
                    db.refresh(question)

            return generated_questions

        except Exception:

            db.rollback()

            raise

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