import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.services.interview_planner.schemas.interview_plan import InterviewPlan
from app.services.interview_planner.schemas.interview_phase import InterviewPhase
from app.services.interview_planner.schemas.interview_objective import InterviewObjective
from app.services.question_selection.selector import QuestionSelector
from app.services.question_selection.schemas.question_selection import QuestionSelection
from app.services.question_selection.schemas.selected_question import SelectedQuestion
from app.services.question_selection.repository import QuestionRepository
from app.shared.enums import ExperienceLevel, QuestionCategory, DifficultyLevel
from app.models.question_bank import QuestionBank
from pydantic import ValidationError

def test_question_selector_success():
    db = MagicMock(spec=Session)
    
    mock_repo = MagicMock(spec=QuestionRepository)
    
    # Mock QuestionBank model
    mock_question = MagicMock(spec=QuestionBank)
    mock_question.id = 100
    mock_question.question_text = "What is Python?"
    mock_question.category = QuestionCategory.TECHNICAL
    mock_question.difficulty = DifficultyLevel.MEDIUM
    
    mock_repo.find_best_questions.return_value = [mock_question]
    
    # Construct InterviewPlan
    objective = InterviewObjective(name="Python", description="Eval Python", priority=10)
    phase = InterviewPhase(
        name="Technical", 
        description="Tech phase", 
        ordering=1, 
        allocated_minutes=20, 
        objectives=[objective]
    )
    plan = InterviewPlan(
        phases=[phase], 
        total_duration_minutes=60, 
        role="Backend", 
        experience_level=ExperienceLevel.MID
    )
    
    selector = QuestionSelector(repository=mock_repo)
    selection = selector.select_questions(db, plan)
    
    assert isinstance(selection, QuestionSelection)
    assert selection.total_questions == 1
    assert len(selection.selected_questions) == 1
    
    selected = selection.selected_questions[0]
    assert isinstance(selected, SelectedQuestion)
    assert selected.question_id == 100
    assert selected.question_text == "What is Python?"
    assert selected.category == QuestionCategory.TECHNICAL
    assert selected.difficulty == DifficultyLevel.MEDIUM
    assert selected.ordering == 1
    assert selected.objective_name == "Python"
    
    # Verify repository was called correctly
    mock_repo.find_best_questions.assert_called_once_with(
        db=db,
        role="Backend",
        experience_level=ExperienceLevel.MID,
        objective=objective,
        limit=1
    )

def test_selected_question_immutability():
    question = SelectedQuestion(
        question_id=1,
        question_text="Test?",
        category=QuestionCategory.BEHAVIORAL,
        difficulty=DifficultyLevel.EASY,
        ordering=1,
        objective_name="Teamwork"
    )
    
    with pytest.raises(ValidationError):
        question.question_text = "Mutated?"
