import json
from app.ai.llm.prompts.base import Prompt, PromptVersion
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation

class AnswerEvaluationPromptBuilder:
    """
    Builder for the Answer Evaluation Prompt.
    Produces an immutable Prompt aggregate.
    """
    
    VERSION = PromptVersion(major=1, minor=0)
    NAME = "answer_evaluation"

    @classmethod
    def build(
        cls,
        question_text: str,
        answer_text: str,
        metrics: AnswerEvaluation,
        interview_context: str | None = None
    ) -> Prompt:
        
        system_prompt = (
            "You are an expert technical interviewer evaluating a candidate's answer. "
            "Your task is to provide qualitative narrative feedback based on the candidate's answer "
            "and the provided deterministic evaluation metrics.\n\n"
            "DO NOT generate, calculate, or modify the quantitative technical scores, keyword coverage, "
            "concept coverage, or completeness. These are deterministic facts that have already been calculated. "
            "Your role is strictly to interpret and explain these facts.\n\n"
            "You MUST output ONLY valid JSON matching the following schema exactly. Do not wrap it in markdown block quotes:\n"
            "{\n"
            '  "strengths": [\n'
            '    {\n'
            '      "category": "Broad category of the observation",\n'
            '      "observation": "Specific qualitative finding",\n'
            '      "evidence": "Optional quote or evidence from the answer"\n'
            '    }\n'
            '  ],\n'
            '  "weaknesses": [\n'
            '    {\n'
            '      "category": "Broad category of the observation",\n'
            '      "observation": "Specific qualitative finding",\n'
            '      "evidence": "Optional quote or evidence from the answer"\n'
            '    }\n'
            '  ],\n'
            '  "communication": {\n'
            '    "clarity_rating": "EXCELLENT, GOOD, FAIR, or NEEDS_IMPROVEMENT",\n'
            '    "confidence_rating": "EXCELLENT, GOOD, FAIR, or NEEDS_IMPROVEMENT",\n'
            '    "tone": "Narrative description of the candidate\'s tone",\n'
            '    "feedback": "Detailed narrative feedback on communication skills"\n'
            '  },\n'
            '  "suggestions": [\n'
            '    {\n'
            '      "category": "Category of the suggestion (e.g., Tone, Clarity, Technical Depth)",\n'
            '      "description": "Actionable advice on how to improve",\n'
            '      "example": "Optional example demonstrating the improvement"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        user_prompt = f"Interview Question:\n{question_text}\n\n"
        
        if interview_context:
            user_prompt += f"Interview Context:\n{interview_context}\n\n"
            
        user_prompt += f"Candidate Answer:\n{answer_text}\n\n"
        
        user_prompt += "Deterministic Metrics:\n"
        user_prompt += f"- Keyword Coverage: {metrics.keyword_coverage:.2f}\n"
        user_prompt += f"- Concept Coverage: {metrics.concept_coverage:.2f}\n"
        user_prompt += f"- Completeness: {metrics.completeness:.2f}\n"
        user_prompt += f"- Overall Score: {metrics.overall_score:.2f}\n\n"
        
        user_prompt += "Please provide your qualitative evaluation in strict JSON format matching the requested schema."

        return Prompt(
            name=cls.NAME,
            version=cls.VERSION,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={
                "question_length": len(question_text),
                "answer_length": len(answer_text),
                "has_context": bool(interview_context)
            }
        )
