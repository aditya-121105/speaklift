from sqlalchemy.orm import Session

from app.models.interview_question import (
    InterviewQuestion,
)


from app.services.interview_execution.repository import ExecutionQuestionRepository

class InterviewQuestionRepository(ExecutionQuestionRepository):

    @staticmethod
    def create(
        db: Session,
        question: InterviewQuestion,
    ) -> InterviewQuestion:

        db.add(question)

        db.commit()

        db.refresh(question)

        return question

    @staticmethod
    def create_many(
        db: Session,
        questions: list[InterviewQuestion],
    ) -> list[InterviewQuestion]:

        db.add_all(questions)

        db.commit()

        for question in questions:
            db.refresh(question)

        return questions

    @staticmethod
    def get_by_id(
        db: Session,
        question_id: int,
    ) -> InterviewQuestion | None:

        return (
            db.query(InterviewQuestion)
            .filter(
                InterviewQuestion.id
                == question_id
            )
            .first()
        )

    @staticmethod
    def get_by_session(
        db: Session,
        interview_session_id: int,
    ) -> list[InterviewQuestion]:

        return (
            db.query(InterviewQuestion)
            .filter(
                InterviewQuestion.interview_session_id
                == interview_session_id
            )
            .order_by(
                InterviewQuestion.execution_path
            )
            .all()
        )

    @staticmethod
    def get_first_unasked_question(
            db: Session,
            interview_session_id: int,
    ) -> InterviewQuestion | None:
        return (
            db.query(InterviewQuestion)
            .filter(
                InterviewQuestion.interview_session_id
                == interview_session_id,
                InterviewQuestion.is_asked.is_(False),
            )
            .order_by(
                InterviewQuestion.execution_path
            )
            .first()
        )


    @staticmethod
    def save(
            db: Session,
            question: InterviewQuestion,
    ) -> InterviewQuestion:
        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def mark_as_asked(
        db: Session,
        question_id: int,
    ) -> InterviewQuestion | None:
        question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
        if question:
            question.is_asked = True
            db.commit()
            db.refresh(question)
        return question

