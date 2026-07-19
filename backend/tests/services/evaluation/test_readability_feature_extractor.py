"""
Tests for ReadabilityFeatureExtractor – M2.1 Evaluation Engine Completion
"""

import pytest
from app.services.evaluation.feature_extractors.text.readability_feature_extractor import (
    ReadabilityFeatureExtractor,
)
from app.services.evaluation.schemas.readability_evaluation import ReadabilityEvaluation


@pytest.fixture
def extractor() -> ReadabilityFeatureExtractor:
    return ReadabilityFeatureExtractor()


def test_empty_text_returns_zeros(extractor):
    result = extractor.extract("")
    assert isinstance(result, ReadabilityEvaluation)
    assert result.flesch_reading_ease == 0.0
    assert result.flesch_kincaid_grade == 0.0
    assert result.average_sentence_length == 0.0


def test_simple_text_has_high_reading_ease(extractor):
    """Short, simple words should produce a high FRE score."""
    text = "The cat sat on the mat. It was a big fat cat."
    result = extractor.extract(text)
    assert isinstance(result, ReadabilityEvaluation)
    # Simple sentences should be easy to read
    assert result.flesch_reading_ease > 50.0


def test_complex_text_has_lower_reading_ease(extractor):
    """Polysyllabic academic prose should produce a lower FRE score."""
    text = (
        "The implementation of deterministic evaluation architectures "
        "necessitates comprehensive analysis of computational complexity "
        "and probabilistic disambiguation methodologies."
    )
    result = extractor.extract(text)
    # Complex vocabulary → lower FRE than simple text
    assert result.flesch_reading_ease < 60.0


def test_average_sentence_length_positive(extractor):
    text = "Python is great. I use it every day for data science."
    result = extractor.extract(text)
    assert result.average_sentence_length > 0.0


def test_result_is_immutable(extractor):
    result = extractor.extract("Hello world.")
    with pytest.raises(Exception):
        result.flesch_reading_ease = 0.0


def test_summary_is_non_empty(extractor):
    result = extractor.extract("The quick brown fox jumps over the lazy dog.")
    assert isinstance(result.summary, str)
    assert len(result.summary) > 0


def test_grade_level_is_a_number(extractor):
    """FKGL can be negative for very short texts but must be a float."""
    text = "I work with Python. I build APIs. I deploy to AWS."
    result = extractor.extract(text)
    assert isinstance(result.flesch_kincaid_grade, float)
