import pytest
from app.services.evaluation.engine import DeterministicEvaluationEngine
from app.services.evaluation.schemas.evaluation_request import EvaluationRequest
from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer
from app.services.question_selection.schemas.question_selection import SelectedQuestion
from app.shared.enums import AnswerSource, QuestionCategory, DifficultyLevel

@pytest.fixture
def empty_answer_request():
    return EvaluationRequest(
        submitted_answer=SubmittedAnswer(
            transcript="   ",
            answer_source=AnswerSource.TEXT,
            answer_duration_seconds=10
        ),
        selected_question=SelectedQuestion(
            question_id=1,
            question_text="What is Python?",
            category=QuestionCategory.TECHNICAL,
            difficulty=DifficultyLevel.EASY,
            ordering=1,
            objective_name="Test objective"
        )
    )

@pytest.fixture
def empty_question_request():
    return EvaluationRequest(
        submitted_answer=SubmittedAnswer(
            transcript="Python is a programming language.",
            answer_source=AnswerSource.TEXT,
            answer_duration_seconds=10
        ),
        selected_question=SelectedQuestion(
            question_id=1,
            question_text="   ",
            category=QuestionCategory.TECHNICAL,
            difficulty=DifficultyLevel.EASY,
            ordering=1,
            objective_name="Test objective"
        )
    )

@pytest.fixture
def valid_request():
    return EvaluationRequest(
        submitted_answer=SubmittedAnswer(
            transcript="Python is a programming language.",
            answer_source=AnswerSource.TEXT,
            answer_duration_seconds=10
        ),
        selected_question=SelectedQuestion(
            question_id=1,
            question_text="What is Python?",
            category=QuestionCategory.TECHNICAL,
            difficulty=DifficultyLevel.EASY,
            ordering=1,
            objective_name="Test objective"
        )
    )

@pytest.fixture
def concept_request():
    return EvaluationRequest(
        submitted_answer=SubmittedAnswer(
            transcript="Apple is a company founded by Steve Jobs.",
            answer_source=AnswerSource.TEXT,
            answer_duration_seconds=10
        ),
        selected_question=SelectedQuestion(
            question_id=1,
            question_text="Who founded Apple?",
            category=QuestionCategory.TECHNICAL,
            difficulty=DifficultyLevel.EASY,
            ordering=1,
            objective_name="Test objective"
        )
    )

from app.services.evaluation.feature_extractors.text.text_processor import TextProcessor
from app.services.evaluation.feature_extractors.text.vocabulary_feature_extractor import VocabularyFeatureExtractor

@pytest.fixture
def evaluation_engine():
    return DeterministicEvaluationEngine(
        text_processor=TextProcessor(),
        vocabulary_extractor=VocabularyFeatureExtractor()
    )

def test_empty_answer(evaluation_engine, empty_answer_request):
    result = evaluation_engine.evaluate(empty_answer_request)
    assert result.keyword_coverage == 0.0
    assert result.concept_coverage == 0.0
    assert result.completeness == 0.0
    assert result.overall_score == 0.0
    assert result.vocabulary_statistics == {}

def test_empty_question(evaluation_engine, empty_question_request):
    result = evaluation_engine.evaluate(empty_question_request)
    assert result.keyword_coverage == 0.0
    assert result.concept_coverage == 0.0
    assert result.overall_score == 0.0
    assert result.completeness > 0.0
    assert "unique_lemmas" in result.vocabulary_statistics

def test_keyword_matching(evaluation_engine, valid_request):
    result = evaluation_engine.evaluate(valid_request)
    # Question content word: "python"
    # Answer content words: "python", "programming", "language"
    assert result.keyword_coverage == 1.0
    assert result.concept_coverage == 1.0 # Fallback to keyword_coverage if no entities
    assert result.completeness > 0.0
    assert result.overall_score > 0.0

def test_concept_matching(evaluation_engine, concept_request):
    result = evaluation_engine.evaluate(concept_request)
    # Question entities: "Apple", "Steve Jobs" (depending on spaCy model)
    # Answer entities: "Apple", "Steve Jobs"
    assert result.concept_coverage > 0.0
    assert result.keyword_coverage > 0.0
    assert result.overall_score > 0.0

def test_immutability(evaluation_engine, valid_request):
    result = evaluation_engine.evaluate(valid_request)
    with pytest.raises(Exception): # Pydantic ValidationError or similar
        result.overall_score = 100.0
