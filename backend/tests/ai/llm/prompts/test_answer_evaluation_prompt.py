import pytest
from app.ai.llm.prompts.answer_evaluation_prompt import AnswerEvaluationPromptBuilder
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
from app.ai.llm.prompts.base import PromptVersion

@pytest.fixture
def dummy_metrics():
    return AnswerEvaluation(
        keyword_coverage=0.85,
        concept_coverage=0.90,
        completeness=1.0,
        vocabulary_statistics={"word_count": 50},
        overall_score=0.9
    )

def test_prompt_construction(dummy_metrics):
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="What is a generator in Python?",
        answer_text="It is a function that returns an iterator using yield.",
        metrics=dummy_metrics
    )
    
    assert prompt.name == "answer_evaluation"
    assert prompt.version == PromptVersion(major=1, minor=0)
    
    # Metadata assertions
    assert prompt.metadata["question_length"] > 0
    assert prompt.metadata["answer_length"] > 0
    assert not prompt.metadata["has_context"]
    
def test_prompt_rendering(dummy_metrics):
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="Q1",
        answer_text="A1",
        metrics=dummy_metrics,
        interview_context="Senior Python Dev"
    )
    
    render_result = prompt.render()
    
    assert render_result.system_prompt is not None
    assert "DO NOT generate, calculate, or modify the quantitative technical scores" in render_result.system_prompt
    assert "strengths" in render_result.system_prompt
    assert "weaknesses" in render_result.system_prompt
    assert "communication" in render_result.system_prompt
    assert "suggestions" in render_result.system_prompt
    
    # Check user prompt
    assert "Interview Question:\nQ1" in render_result.user_prompt
    assert "Candidate Answer:\nA1" in render_result.user_prompt
    assert "Interview Context:\nSenior Python Dev" in render_result.user_prompt
    assert "- Keyword Coverage: 0.85" in render_result.user_prompt
    
    # Check metadata
    assert prompt.metadata["has_context"] is True

def test_prompt_immutability(dummy_metrics):
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="Q",
        answer_text="A",
        metrics=dummy_metrics
    )
    
    with pytest.raises(Exception): # Pydantic ValidationError or frozen exception
        prompt.name = "hacked"
