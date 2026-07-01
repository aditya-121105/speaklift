"""
==============================================================================
Question Selector

Purpose:
Select interview questions that satisfy the InterviewPlan.

Responsibilities

✔ Read InterviewPlan
✔ Retrieve questions from Question Bank
✔ Build InterviewQuestion objects

Does NOT

✘ Generate questions
✘ Evaluate answers
✘ Call LLMs

If suitable questions do not exist, later versions will delegate
to the AI Question Generator.

==============================================================================
"""

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

from app.schemas.interview_engine.interview_plan import (
    InterviewPlan,
)

from app.shared.enums import (
    QuestionType,
)


class QuestionSelector:

    @classmethod
    def select_questions(
        cls,
        db: Session,
        interview_session: InterviewSession,
        interview_plan: InterviewPlan,
    ) -> list[InterviewQuestion]:

        selected_questions: list[
            InterviewQuestion
        ] = []

        question_order = 1

        for phase in interview_plan.phases:

            for objective in phase.objectives:

                bank_questions = (
                    QuestionBankRepository.get_questions(
                        db=db,
                        role=interview_session.role,
                        experience_level=(
                            interview_session
                            .experience_level
                        ),
                        category=None,
                        limit=1,
                    )
                )

                if not bank_questions:
                    continue

                bank_question = bank_questions[0]

                bank_question.usage_count += 1

                selected_questions.append(
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
                        question_category=(
                            bank_question.category
                        ),
                        question_order=question_order,
                        is_asked=False,
                    )
                )

                question_order += 1

        return selected_questions