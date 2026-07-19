"""
Tests for ConfidenceFeatureExtractor – M2.1 Evaluation Engine Completion
"""

import pytest
from app.services.evaluation.feature_extractors.text.confidence_feature_extractor import (
    ConfidenceFeatureExtractor,
)
from app.services.evaluation.schemas.confidence_evaluation import ConfidenceEvaluation


@pytest.fixture
def extractor() -> ConfidenceFeatureExtractor:
    return ConfidenceFeatureExtractor()


def test_empty_text_returns_full_confidence(extractor):
    result = extractor.extract("")
    assert isinstance(result, ConfidenceEvaluation)
    assert result.confidence_score == 1.0
    assert result.filler_word_count == 0
    assert result.hedging_phrase_count == 0


def test_clean_answer_has_high_confidence(extractor):
    text = "I implemented a distributed caching layer using Redis to reduce database load."
    result = extractor.extract(text)
    assert result.confidence_score >= 0.9
    assert result.filler_word_count == 0


def test_filler_words_detected(extractor):
    text = "Um, I, uh, worked with Python, you know, and basically built APIs."
    result = extractor.extract(text)
    assert result.filler_word_count >= 2
    assert result.confidence_score < 1.0


def test_hedging_phrases_detected(extractor):
    text = "I think maybe I could use Redis, perhaps, but I'm not sure."
    result = extractor.extract(text)
    assert result.hedging_phrase_count >= 2
    assert result.confidence_score < 1.0


def test_filler_ratio_between_zero_and_one(extractor):
    text = "Um, uh, well, I guess I kind of know Python, basically."
    result = extractor.extract(text)
    assert 0.0 <= result.filler_word_ratio <= 1.0


def test_detected_fillers_populated(extractor):
    text = "Um, well, uh, I think this is correct."
    result = extractor.extract(text)
    assert len(result.detected_fillers) > 0


def test_result_is_immutable(extractor):
    result = extractor.extract("I think this is a good answer.")
    with pytest.raises(Exception):
        result.confidence_score = 1.0


def test_confidence_score_clamped(extractor):
    """Score must always be in [0, 1] regardless of how many fillers appear."""
    very_hedgy = " ".join(
        ["um I think maybe I'm not sure perhaps"] * 10
    )
    result = extractor.extract(very_hedgy)
    assert 0.0 <= result.confidence_score <= 1.0


def test_summary_populated(extractor):
    result = extractor.extract("I built a REST API with FastAPI and PostgreSQL.")
    assert isinstance(result.summary, str)
    assert len(result.summary) > 0
