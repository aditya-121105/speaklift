import json
from typing import List, Dict, Any
from app.ai.llm.prompts.base import Prompt, PromptVersion

class ReportPromptBuilder:
    """Builds prompts for generating interview reports based on aggregated evaluation data."""
    
    @staticmethod
    def build_report_prompt(
        session_id: int,
        context_data: Dict[str, Any],
        questions_and_evals: List[Dict[str, Any]]
    ) -> Prompt:
        
        system_prompt = (
            "You are an expert technical interviewer and hiring manager. "
            "You are tasked with writing a comprehensive evaluation report for a candidate "
            "who has just completed a technical interview. "
            "You will be provided with the aggregated deterministic metrics and per-question AI feedback. "
            "Analyze the data and produce an objective, evidence-based assessment. "
            "Respond ONLY with valid JSON conforming strictly to the requested schema. Do not include markdown blocks."
        )

        user_prompt = f"""
Candidate Interview Session ID: {session_id}

### Aggregated Interview Statistics
{json.dumps(context_data, indent=2)}

### Question-by-Question Evaluations
"""
        
        for q_eval in questions_and_evals:
            user_prompt += f"\n--- Question {q_eval['planned_order']} ({q_eval['execution_path']}) ---\n"
            user_prompt += f"Q: {q_eval['question_text']}\n"
            user_prompt += f"Category: {q_eval['category']}\n"
            user_prompt += f"Answer Transcript: {q_eval['answer_transcript']}\n"
            user_prompt += f"Score: {q_eval['score']}/100\n"
            user_prompt += f"Strengths: {', '.join(q_eval.get('strengths', []))}\n"
            user_prompt += f"Weaknesses: {', '.join(q_eval.get('weaknesses', []))}\n"
            
        user_prompt += """
Based on the evidence above, generate the final report including:
1. Executive Summary (overall_performance, confidence_level, narrative)
2. Competencies (technical, behavioral, communication - rate each and provide evidence)
3. Hiring Recommendation (decision: HIRE, HIRE_WITH_RESERVATIONS, BORDERLINE, NO_HIRE) with reasoning and evidence.
4. Learning Roadmap (prioritized_skill_gaps, learning_sequence).

Output valid JSON matching the AIReportGenerationResult schema.
"""

        return Prompt(
            name="generate_interview_report",
            version=PromptVersion(major=1, minor=0),
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
