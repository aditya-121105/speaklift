from sqlalchemy.orm import Session
from app.services.interview_planner.schemas.interview_plan import InterviewPlan
from app.services.question_selection.repository import QuestionRepository
from app.services.question_selection.schemas.question_selection import QuestionSelection
from app.services.question_selection.schemas.selected_question import SelectedQuestion

class QuestionSelector:
    """
    Stateless deterministic service for selecting questions from the Question Bank.
    """
    
    def __init__(self, repository: QuestionRepository):
        self._repository = repository
        
    def select_questions(self, db: Session, plan: InterviewPlan) -> QuestionSelection:
        selected_questions = []
        ordering = 1
        
        for phase in plan.phases:
            for objective in phase.objectives:
                # Primary attempt: Find best questions for the objective
                bank_questions = self._repository.find_best_questions(
                    db=db,
                    role=plan.role,
                    experience_level=plan.experience_level,
                    objective=objective,
                    limit=1
                )
                
                if not bank_questions:
                    # Fallback: Find any question for the role/level
                    bank_questions = self._repository.get_questions(
                        db=db,
                        role=plan.role,
                        experience_level=plan.experience_level,
                        limit=1
                    )
                
                if bank_questions:
                    bank_question = bank_questions[0]
                    # We do NOT mutate usage_count here. The business layer must be pure.
                    
                    selected_questions.append(
                        SelectedQuestion(
                            question_id=bank_question.id,
                            question_text=bank_question.question_text,
                            category=bank_question.category,
                            difficulty=bank_question.difficulty,
                            ordering=ordering,
                            objective_name=objective.name
                        )
                    )
                    ordering += 1
                    
        return QuestionSelection(
            selected_questions=selected_questions,
            total_questions=len(selected_questions)
        )
