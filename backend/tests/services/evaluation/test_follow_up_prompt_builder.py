"""
Tests for FollowUpPromptBuilder – M2.2 Adaptive Interview System
"""

import pytest
from app.ai.llm.prompts.follow_up_prompt import FollowUpPromptBuilder
from app.services.interview_execution.schemas.adaptive_decision import DecisionReason
from app.ai.llm.prompts.base import PromptVersion


@pytest.mark.parametrize("reason", [
    DecisionReason.WEAK_KEYWORD_COVERAGE,
    DecisionReason.WEAK_CONCEPT_COVERAGE,
    DecisionReason.WEAK_SEMANTIC_SIMILARITY,
    DecisionReason.LOW_CONFIDENCE,
    DecisionReason.INCOMPLETE_ANSWER,
])
def test_prompt_built_for_all_reasons(reason):
    prompt = FollowUpPromptBuilder.build(
        original_question="What is Python?",
        candidate_answer="Um, Python is kind of like... a thing.",
        weak_reason=reason,
        category="TECHNICAL",
        objective_name="Python fundamentals",
    )
    assert prompt.name == "follow_up_generation"
    assert isinstance(prompt.version, PromptVersion)
    assert prompt.system_prompt is not None
    assert "follow_up_question" in prompt.system_prompt
    assert "What is Python?" in prompt.user_prompt
    assert "Um, Python" in prompt.user_prompt


def test_prompt_metadata_contains_reason():
    prompt = FollowUpPromptBuilder.build(
        original_question="Explain REST.",
        candidate_answer="It stands for something.",
        weak_reason=DecisionReason.WEAK_KEYWORD_COVERAGE,
        category="TECHNICAL",
        objective_name="API design",
    )
    assert prompt.metadata["weak_reason"] == DecisionReason.WEAK_KEYWORD_COVERAGE.value
    assert prompt.metadata["category"] == "TECHNICAL"


def test_prompt_is_immutable():
    prompt = FollowUpPromptBuilder.build(
        original_question="Q",
        candidate_answer="A",
        weak_reason=DecisionReason.INCOMPLETE_ANSWER,
        category="BEHAVIORAL",
        objective_name="obj",
    )
    with pytest.raises(Exception):
        prompt.name = "hacked"  # type: ignore[misc]
