from sqlalchemy.orm import Session
from app.models.answer_evaluation import AnswerEvaluation

class AnswerEvaluationRepository:
    """
    Data access layer for answer-level evaluations.
    """

    @staticmethod
    def create(db: Session, evaluation: AnswerEvaluation) -> AnswerEvaluation:
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation

    @staticmethod
    def get_by_id(db: Session, evaluation_id: int) -> AnswerEvaluation | None:
        return db.query(AnswerEvaluation).filter(AnswerEvaluation.id == evaluation_id).first()

    @staticmethod
    def get_by_answer_id(db: Session, answer_id: int) -> AnswerEvaluation | None:
        return db.query(AnswerEvaluation).filter(AnswerEvaluation.interview_answer_id == answer_id).first()
