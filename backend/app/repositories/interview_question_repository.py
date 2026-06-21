from sqlalchemy.orm import Session

from app.models.interview_question import (
    InterviewQuestion,
)


class InterviewQuestionRepository:

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
                InterviewQuestion.question_order
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
                InterviewQuestion.question_order
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