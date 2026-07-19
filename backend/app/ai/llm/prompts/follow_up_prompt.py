"""
==============================================================================
Module:
    Follow-Up Question Generation Prompt Builder

Milestone:
    M2.2 – Adaptive Interview System

Purpose:
    Builds the LLM prompt that generates a contextual follow-up question
    based on the original question, the candidate's answer, and the
    identified weak signals.

Design contract with the LLM
-----------------------------
The LLM receives:
  - The original interview question.
  - The candidate's transcript.
  - A short description of why a follow-up is needed (weak signals).
  - The objective/category context.

The LLM MUST return a single JSON object:
    {"follow_up_question": "<question text>"}

Only one follow-up is generated per invocation.
==============================================================================
"""

from app.ai.llm.prompts.base import Prompt, PromptVersion
from app.services.interview_execution.schemas.adaptive_decision import DecisionReason


# Human-readable descriptions of each weak reason for the LLM
_REASON_DESCRIPTIONS: dict[DecisionReason, str] = {
    DecisionReason.WEAK_KEYWORD_COVERAGE: (
        "The answer did not address the core technical keywords from the question."
    ),
    DecisionReason.WEAK_CONCEPT_COVERAGE: (
        "The answer missed important concepts or entities referenced in the question."
    ),
    DecisionReason.WEAK_SEMANTIC_SIMILARITY: (
        "The answer was not semantically relevant to the question that was asked."
    ),
    DecisionReason.LOW_CONFIDENCE: (
        "The candidate expressed significant uncertainty or used many hedging phrases."
    ),
    DecisionReason.INCOMPLETE_ANSWER: (
        "The answer was too brief to demonstrate adequate understanding of the topic."
    ),
}


class FollowUpPromptBuilder:
    """
    Builds the Prompt for follow-up question generation.
    """

    VERSION = PromptVersion(major=1, minor=0)
    NAME = "follow_up_generation"

    @classmethod
    def build(
        cls,
        original_question: str,
        candidate_answer: str,
        weak_reason: DecisionReason,
        category: str,
        objective_name: str,
    ) -> Prompt:
        reason_desc = _REASON_DESCRIPTIONS.get(
            weak_reason,
            "The answer was not sufficiently complete.",
        )

        system_prompt = (
            "You are an expert technical interviewer conducting a real-time interview. "
            "The candidate has just answered a question inadequately. "
            "Your task is to generate ONE concise follow-up question that:\n"
            "  1. References the candidate's previous answer directly.\n"
            "  2. Probes the specific gap identified.\n"
            "  3. Remains relevant to the original topic and interview objective.\n"
            "  4. Is phrased naturally, as a human interviewer would ask.\n"
            "  5. Does NOT simply repeat the original question.\n\n"
            "You MUST output ONLY valid JSON with exactly one field:\n"
            '  {"follow_up_question": "<your question here>"}\n\n'
            "Do not include any explanation, markdown, or additional text."
        )

        user_prompt = (
            f"Interview Category: {category}\n"
            f"Interview Objective: {objective_name}\n\n"
            f"Original Question:\n{original_question}\n\n"
            f"Candidate's Answer:\n{candidate_answer}\n\n"
            f"Identified Gap:\n{reason_desc}\n\n"
            "Generate a follow-up question that addresses this specific gap."
        )

        return Prompt(
            name=cls.NAME,
            version=cls.VERSION,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={
                "weak_reason": weak_reason.value,
                "category": category,
                "objective": objective_name,
            },
        )
