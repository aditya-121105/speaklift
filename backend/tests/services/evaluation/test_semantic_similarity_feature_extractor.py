"""
Tests for SemanticSimilarityFeatureExtractor – M2.1 Evaluation Engine Completion

NOTE: These tests load the BAAI/bge-base-en-v1.5 SentenceTransformer model,
which is cached locally. Tests are marked with `pytest.mark.slow` and can be
excluded with:
    pytest -m "not slow"
"""

import pytest
from app.services.evaluation.feature_extractors.text.semantic_similarity_feature_extractor import (
    SemanticSimilarityFeatureExtractor,
)
from app.services.evaluation.schemas.semantic_evaluation import SemanticEvaluation


@pytest.fixture
def extractor() -> SemanticSimilarityFeatureExtractor:
    return SemanticSimilarityFeatureExtractor()


@pytest.mark.slow
def test_empty_question_returns_zero(extractor):
    result = extractor.extract("", "Some answer text")
    assert isinstance(result, SemanticEvaluation)
    assert result.cosine_similarity == 0.0
    assert result.relevance_score == 0.0


@pytest.mark.slow
def test_empty_answer_returns_zero(extractor):
    result = extractor.extract("What is Python?", "")
    assert result.cosine_similarity == 0.0
    assert result.relevance_score == 0.0


@pytest.mark.slow
def test_identical_text_has_high_similarity(extractor):
    text = "Python is a high-level programming language."
    result = extractor.extract(text, text)
    assert result.cosine_similarity > 0.95
    assert result.relevance_score > 0.95


@pytest.mark.slow
def test_relevant_answer_has_moderate_to_high_similarity(extractor):
    question = "What is Python?"
    answer = "Python is a popular programming language often used in data science and web development."
    result = extractor.extract(question, answer)
    assert result.relevance_score >= 0.5


@pytest.mark.slow
def test_irrelevant_answer_has_low_similarity(extractor):
    question = "What is Python?"
    answer = "The weather in Mumbai today is sunny and warm."
    result = extractor.extract(question, answer)
    # Unrelated topic → lower relevance
    relevant = extractor.extract(question, "Python is a programming language.")
    assert result.relevance_score < relevant.relevance_score


@pytest.mark.slow
def test_relevance_score_in_range(extractor):
    result = extractor.extract(
        "Explain REST API design.",
        "REST stands for Representational State Transfer. It uses HTTP verbs.",
    )
    assert 0.0 <= result.relevance_score <= 1.0
    assert -1.0 <= result.cosine_similarity <= 1.0


@pytest.mark.slow
def test_result_is_immutable(extractor):
    result = extractor.extract("What is Python?", "Python is a language.")
    with pytest.raises(Exception):
        result.relevance_score = 0.0


@pytest.mark.slow
def test_summary_non_empty(extractor):
    result = extractor.extract("What is Python?", "Python is a programming language.")
    assert isinstance(result.summary, str)
    assert len(result.summary) > 0
