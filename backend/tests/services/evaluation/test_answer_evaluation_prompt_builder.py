"""
Tests for AnswerEvaluationPromptBuilder – M2.1 Evaluation Engine Completion

Validates that all deterministic metrics (core + extended) are injected
into the user prompt.
"""

import pytest
from app.ai.llm.prompts.answer_evaluation_prompt import AnswerEvaluationPromptBuilder
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
from app.services.evaluation.schemas.grammar_evaluation import GrammarEvaluation
from app.services.evaluation.schemas.readability_evaluation import ReadabilityEvaluation
from app.services.evaluation.schemas.confidence_evaluation import ConfidenceEvaluation
from app.services.evaluation.schemas.semantic_evaluation import SemanticEvaluation


def _base_metrics(**kwargs) -> AnswerEvaluation:
    defaults = dict(
        keyword_coverage=0.8,
        concept_coverage=0.7,
        completeness=0.6,
        vocabulary_statistics={
            "vocabulary_richness": 0.65,
            "lexical_density": 0.55,
            "unique_lemmas": 18,
            "stop_word_ratio": 0.30,
        },
        overall_score=0.72,
    )
    defaults.update(kwargs)
    return AnswerEvaluation(**defaults)


def test_core_metrics_present_in_prompt():
    metrics = _base_metrics()
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="What is Python?",
        answer_text="Python is a high-level programming language.",
        metrics=metrics,
    )
    assert "Keyword Coverage" in prompt.user_prompt
    assert "Concept Coverage" in prompt.user_prompt
    assert "Completeness" in prompt.user_prompt
    assert "Overall Score" in prompt.user_prompt


def test_vocabulary_statistics_injected():
    metrics = _base_metrics()
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="What is Python?",
        answer_text="Python is a language.",
        metrics=metrics,
    )
    assert "Vocabulary Richness" in prompt.user_prompt
    assert "Lexical Density" in prompt.user_prompt


def test_grammar_metrics_injected_when_present():
    grammar = GrammarEvaluation(
        grammar_error_count=1,
        grammar_quality_score=0.9,
        error_rate_per_sentence=0.5,
        summary="Minor issues.",
    )
    metrics = _base_metrics(grammar=grammar)
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="Explain OOP.",
        answer_text="OOP stands for object oriented programming.",
        metrics=metrics,
    )
    assert "Grammar Quality Score" in prompt.user_prompt
    assert "Grammar Error Count" in prompt.user_prompt


def test_readability_metrics_injected_when_present():
    readability = ReadabilityEvaluation(
        flesch_reading_ease=72.5,
        flesch_kincaid_grade=6.0,
        average_sentence_length=14.0,
        average_syllables_per_word=1.5,
        summary="Easy.",
    )
    metrics = _base_metrics(readability=readability)
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="Describe REST.",
        answer_text="REST is an architectural style.",
        metrics=metrics,
    )
    assert "Flesch Reading Ease" in prompt.user_prompt
    assert "Flesch-Kincaid Grade" in prompt.user_prompt


def test_confidence_metrics_injected_when_present():
    confidence = ConfidenceEvaluation(
        filler_word_count=3,
        hedging_phrase_count=2,
        filler_word_ratio=0.12,
        detected_fillers=["um", "uh", "i think"],
        confidence_score=0.7,
        summary="Some hedging detected.",
    )
    metrics = _base_metrics(confidence=confidence)
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="Tell me about Docker.",
        answer_text="Um, I think Docker is like a container platform.",
        metrics=metrics,
    )
    assert "Confidence Score" in prompt.user_prompt
    assert "Filler Words Detected" in prompt.user_prompt


def test_semantic_metrics_injected_when_present():
    semantic = SemanticEvaluation(
        cosine_similarity=0.82,
        relevance_score=0.82,
        summary="Highly Relevant.",
    )
    metrics = _base_metrics(semantic_similarity=semantic)
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="What is Kubernetes?",
        answer_text="Kubernetes orchestrates containers across a cluster.",
        metrics=metrics,
    )
    assert "Cosine Similarity" in prompt.user_prompt
    assert "Relevance Score" in prompt.user_prompt


def test_no_extended_metrics_produces_minimal_prompt():
    """When only core metrics are present, extended sections should be absent."""
    metrics = _base_metrics()
    prompt = AnswerEvaluationPromptBuilder.build(
        question_text="What is Python?",
        answer_text="Python is a language.",
        metrics=metrics,
    )
    assert "Grammar Quality Score" not in prompt.user_prompt
    assert "Flesch Reading Ease" not in prompt.user_prompt
    assert "Confidence Score" not in prompt.user_prompt
    assert "Cosine Similarity" not in prompt.user_prompt


def test_prompt_version_is_1_1():
    metrics = _base_metrics()
    prompt = AnswerEvaluationPromptBuilder.build("Q", "A", metrics)
    assert prompt.version.major == 1
    assert prompt.version.minor == 1


def test_metadata_flags_reflect_extended_metrics():
    semantic = SemanticEvaluation(
        cosine_similarity=0.7, relevance_score=0.7, summary="Relevant."
    )
    metrics = _base_metrics(semantic_similarity=semantic)
    prompt = AnswerEvaluationPromptBuilder.build("Q", "A", metrics)
    assert prompt.metadata["has_semantic_metrics"] is True
    assert prompt.metadata["has_grammar_metrics"] is False
