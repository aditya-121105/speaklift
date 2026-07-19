"""
==============================================================================
Module:
    Answer Evaluation Prompt Builder

Milestone:
    M2.1 – Evaluation Engine Completion  (enriched from M1 baseline)

Changes
-------
- Injects vocabulary_statistics (richness, lexical density) into user prompt.
- Injects grammar quality score and error count when available.
- Injects readability metrics (FRE, FKGL) when available.
- Injects confidence score and filler-word count when available.
- Injects semantic similarity relevance score when available.
- Retains the deterministic contract with the LLM:
    the model MUST NOT recalculate quantitative values.

Responsibilities:
    ✔ Build an immutable Prompt aggregate for the evaluation LLM
    ✔ Expose all deterministic metrics as numeric context
    ✔ Keep the system prompt concise and unambiguous

Does NOT:
    ✘ Invoke the LLM
    ✘ Access the database
    ✘ Modify AnswerEvaluation data
==============================================================================
"""

from app.ai.llm.prompts.base import Prompt, PromptVersion
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation


class AnswerEvaluationPromptBuilder:
    """
    Builder for the Answer Evaluation Prompt.
    Produces an immutable Prompt aggregate.
    """

    VERSION = PromptVersion(major=1, minor=1)
    NAME = "answer_evaluation"

    @classmethod
    def build(
        cls,
        question_text: str,
        answer_text: str,
        metrics: AnswerEvaluation,
        interview_context: str | None = None,
    ) -> Prompt:
        system_prompt = (
            "You are an expert technical interviewer evaluating a candidate's answer. "
            "Your task is to provide qualitative narrative feedback based on the candidate's answer "
            "and the provided deterministic evaluation metrics.\n\n"
            "DO NOT generate, calculate, or modify the quantitative scores supplied to you. "
            "These are deterministic facts already calculated by the system. "
            "Your role is strictly to interpret and explain these facts.\n\n"
            "You MUST output ONLY valid JSON matching the following schema exactly. "
            "Do not wrap it in markdown block quotes:\n"
            "{\n"
            '  "strengths": [\n'
            '    {\n'
            '      "category": "Broad category of the observation",\n'
            '      "observation": "Specific qualitative finding",\n'
            '      "evidence": "Optional quote or evidence from the answer"\n'
            "    }\n"
            "  ],\n"
            '  "weaknesses": [\n'
            '    {\n'
            '      "category": "Broad category of the observation",\n'
            '      "observation": "Specific qualitative finding",\n'
            '      "evidence": "Optional quote or evidence from the answer"\n'
            "    }\n"
            "  ],\n"
            '  "communication": {\n'
            '    "clarity_rating": "EXCELLENT, GOOD, FAIR, or NEEDS_IMPROVEMENT",\n'
            '    "confidence_rating": "EXCELLENT, GOOD, FAIR, or NEEDS_IMPROVEMENT",\n'
            '    "tone": "Narrative description of the candidate\'s tone",\n'
            '    "feedback": "Detailed narrative feedback on communication skills"\n'
            "  },\n"
            '  "suggestions": [\n'
            '    {\n'
            '      "category": "Category of the suggestion (e.g., Tone, Clarity, Technical Depth)",\n'
            '      "description": "Actionable advice on how to improve",\n'
            '      "example": "Optional example demonstrating the improvement"\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        # --- User prompt: question + answer ---
        user_prompt = f"Interview Question:\n{question_text}\n\n"

        if interview_context:
            user_prompt += f"Interview Context:\n{interview_context}\n\n"

        user_prompt += f"Candidate Answer:\n{answer_text}\n\n"

        # --- Core deterministic metrics (always present) ---
        user_prompt += "Deterministic Metrics:\n"
        user_prompt += f"- Keyword Coverage:  {metrics.keyword_coverage:.2f}\n"
        user_prompt += f"- Concept Coverage:  {metrics.concept_coverage:.2f}\n"
        user_prompt += f"- Completeness:      {metrics.completeness:.2f}\n"
        user_prompt += f"- Overall Score:     {metrics.overall_score:.2f}\n"

        # --- Vocabulary statistics (always extracted, now always exposed) ---
        vs = metrics.vocabulary_statistics
        if vs:
            user_prompt += "\nVocabulary Metrics:\n"
            if "vocabulary_richness" in vs:
                user_prompt += f"- Vocabulary Richness: {vs['vocabulary_richness']:.2f}\n"
            if "lexical_density" in vs:
                user_prompt += f"- Lexical Density:     {vs['lexical_density']:.2f}\n"
            if "unique_lemmas" in vs:
                user_prompt += f"- Unique Lemmas:       {vs['unique_lemmas']}\n"
            if "stop_word_ratio" in vs:
                user_prompt += f"- Stop-Word Ratio:     {vs['stop_word_ratio']:.2f}\n"

        # --- Grammar (optional / M2.1) ---
        if metrics.grammar is not None:
            g = metrics.grammar
            user_prompt += "\nGrammar Metrics:\n"
            user_prompt += f"- Grammar Quality Score: {g.grammar_quality_score:.2f}\n"
            user_prompt += f"- Grammar Error Count:   {g.grammar_error_count}\n"
            user_prompt += f"- Errors per Sentence:   {g.error_rate_per_sentence:.2f}\n"

        # --- Readability (optional / M2.1) ---
        if metrics.readability is not None:
            r = metrics.readability
            user_prompt += "\nReadability Metrics:\n"
            user_prompt += f"- Flesch Reading Ease:    {r.flesch_reading_ease:.1f}\n"
            user_prompt += f"- Flesch-Kincaid Grade:   {r.flesch_kincaid_grade:.1f}\n"
            user_prompt += f"- Avg Sentence Length:    {r.average_sentence_length:.1f} words\n"
            user_prompt += f"- Avg Syllables/Word:     {r.average_syllables_per_word:.2f}\n"

        # --- Confidence (optional / M2.1) ---
        if metrics.confidence is not None:
            c = metrics.confidence
            user_prompt += "\nConfidence Metrics:\n"
            user_prompt += f"- Confidence Score:       {c.confidence_score:.2f}\n"
            user_prompt += f"- Filler Words Detected:  {c.filler_word_count}\n"
            user_prompt += f"- Hedging Phrases:        {c.hedging_phrase_count}\n"
            if c.detected_fillers:
                samples = ", ".join(c.detected_fillers[:6])
                user_prompt += f"- Detected Indicators:    {samples}\n"

        # --- Semantic similarity (optional / M2.1) ---
        if metrics.semantic_similarity is not None:
            s = metrics.semantic_similarity
            user_prompt += "\nSemantic Relevance:\n"
            user_prompt += f"- Cosine Similarity:      {s.cosine_similarity:.3f}\n"
            user_prompt += f"- Relevance Score:        {s.relevance_score:.3f}\n"

        user_prompt += (
            "\nPlease provide your qualitative evaluation in strict JSON "
            "format matching the requested schema."
        )

        return Prompt(
            name=cls.NAME,
            version=cls.VERSION,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={
                "question_length": len(question_text),
                "answer_length": len(answer_text),
                "has_context": bool(interview_context),
                "has_grammar_metrics": metrics.grammar is not None,
                "has_readability_metrics": metrics.readability is not None,
                "has_confidence_metrics": metrics.confidence is not None,
                "has_semantic_metrics": metrics.semantic_similarity is not None,
            },
        )
