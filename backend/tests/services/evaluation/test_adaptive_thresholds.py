"""
Tests for AdaptiveThresholds – M2.2 Adaptive Interview System
"""

import pytest
from app.services.interview_execution.adaptive_thresholds import AdaptiveThresholds


def test_default_thresholds_valid():
    t = AdaptiveThresholds()
    assert t.min_keyword_coverage == 0.40
    assert t.min_semantic_similarity == 0.50
    assert t.max_follow_ups_per_primary == 2
    assert t.max_total_questions == 20
    assert t.weak_metric_threshold == 2


def test_custom_thresholds():
    t = AdaptiveThresholds(
        min_keyword_coverage=0.6,
        max_follow_ups_per_primary=3,
        max_total_questions=10,
    )
    assert t.min_keyword_coverage == 0.6
    assert t.max_follow_ups_per_primary == 3
    assert t.max_total_questions == 10


def test_invalid_coverage_raises():
    with pytest.raises(ValueError):
        AdaptiveThresholds(min_keyword_coverage=1.5)


def test_invalid_max_follow_ups_raises():
    with pytest.raises(ValueError):
        AdaptiveThresholds(max_follow_ups_per_primary=-1)


def test_invalid_max_questions_raises():
    with pytest.raises(ValueError):
        AdaptiveThresholds(max_total_questions=0)


def test_invalid_weak_threshold_raises():
    with pytest.raises(ValueError):
        AdaptiveThresholds(weak_metric_threshold=0)


def test_thresholds_are_frozen():
    t = AdaptiveThresholds()
    with pytest.raises(Exception):
        t.min_keyword_coverage = 0.9  # type: ignore[misc]
