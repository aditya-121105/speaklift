"""
==============================================================================
Module:
    Follow-Up Generation Service

Milestone:
    M2.2 – Adaptive Interview System

Purpose:
    Generates a contextual follow-up question text by invoking the LLM
    and returns a fully constructed InterviewQuestion ready for persistence.

Responsibilities:
    ✔ Build the follow-up prompt via FollowUpPromptBuilder
    ✔ Invoke LLMService.generate_text()
    ✔ Gracefully degrade to a template fallback if LLM fails
    ✔ Construct an InterviewQuestion with:
        - question_type: QuestionType.FOLLOW_UP
        - parent_question_id set to the originating primary question
        - execution_path assigned correctly (e.g. 01.01)

Does NOT:
    ✘ Persist the question (responsibility of execution service)
    ✘ Trigger evaluation (already done upstream)
    ✘ Access the database directly
==============================================================================
"""

import logging
from pydantic import BaseModel, Field

from app.ai.llm.services.llm_service import LLMService
from app.ai.llm.prompts.follow_up_prompt import FollowUpPromptBuilder
from app.models.interview_question import InterviewQuestion
from app.services.interview_execution.schemas.adaptive_decision import DecisionReason
from app.shared.enums import QuestionType

logger = logging.getLogger(__name__)

# LLM response schema for follow-up generation
class _FollowUpResponse(BaseModel):
    follow_up_question: str = Field(description="The generated follow-up question text.")


class FollowUpGenerationService:
    """
    Generates a contextual follow-up InterviewQuestion using the LLM.

    Parameters
    ----------
    llm_service : LLMService
        The application's LLM orchestration service.
    max_tokens : int
        Maximum tokens for the generated follow-up question.
    temperature : float
        LLM temperature for follow-up generation (lower = more focused).
    """

    _FALLBACK_TEMPLATES: dict[DecisionReason, str] = {
        DecisionReason.WEAK_KEYWORD_COVERAGE: (
            "Could you elaborate further on the technical aspects of your answer?"
        ),
        DecisionReason.WEAK_CONCEPT_COVERAGE: (
            "Can you explain the key concepts in more detail?"
        ),
        DecisionReason.WEAK_SEMANTIC_SIMILARITY: (
            "Your answer seems to be off-topic. Could you address the original question more directly?"
        ),
        DecisionReason.LOW_CONFIDENCE: (
            "You seemed uncertain. Could you clarify your understanding of this topic?"
        ),
        DecisionReason.INCOMPLETE_ANSWER: (
            "Could you expand on your answer and provide more detail?"
        ),
    }

    def __init__(
        self,
        llm_service: LLMService,
        max_tokens: int = 150,
        temperature: float = 0.4,
    ) -> None:
        self._llm_service = llm_service
        self._max_tokens = max_tokens
        self._temperature = temperature

    def generate(
        self,
        *,
        session_id: int,
        parent_question: InterviewQuestion,
        candidate_answer: str,
        weak_reason: DecisionReason,
        objective_name: str,
        planned_order: int,
        execution_path: str,
    ) -> InterviewQuestion:
        """
        Generate and return an InterviewQuestion follow-up (not yet persisted).

        Parameters
        ----------
        session_id       : The interview session id.
        parent_question  : The primary question that triggered the follow-up.
        candidate_answer : The transcript of the candidate's inadequate answer.
        weak_reason      : The primary weak signal that drove the decision.
        objective_name   : The interview objective for prompt context.
        planned_order    : The planned order inherited from parent.
        execution_path   : The new materialized execution path.

        Returns
        -------
        InterviewQuestion (not persisted)
        """
        question_text = self._generate_text(parent_question, candidate_answer, weak_reason, objective_name)

        return InterviewQuestion(
            interview_session_id=session_id,
            parent_question_id=parent_question.id,
            question_text=question_text,
            question_type=QuestionType.FOLLOW_UP,
            question_category=parent_question.question_category,
            planned_order=planned_order,
            execution_path=execution_path,
            is_asked=False,
        )

    def _generate_text(
        self,
        parent_question: InterviewQuestion,
        candidate_answer: str,
        weak_reason: DecisionReason,
        objective_name: str,
    ) -> str:
        """
        Call LLMService and return the follow-up question text.
        Falls back to a hardcoded template if LLM invocation fails.
        """
        try:
            prompt = FollowUpPromptBuilder.build(
                original_question=parent_question.question_text,
                candidate_answer=candidate_answer,
                weak_reason=weak_reason,
                category=parent_question.question_category.value,
                objective_name=objective_name,
            )
            response = self._llm_service.generate_json(
                prompt,
                _FollowUpResponse,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
            )
            text = response.follow_up_question.strip()
            if text:
                return text
        except Exception as exc:
            logger.warning(
                "Follow-up generation LLM call failed (%s). Using template fallback.",
                exc,
            )

        # Graceful degradation
        return self._FALLBACK_TEMPLATES.get(
            weak_reason,
            "Could you elaborate further on your previous answer?",
        )
