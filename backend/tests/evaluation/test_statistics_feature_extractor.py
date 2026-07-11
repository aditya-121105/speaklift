"""
==============================================================================
Tests:
    Statistics Feature Extractor

Purpose:
    Unit tests for statistical feature extraction.
==============================================================================
"""

from app.services.evaluation.feature_extractors.text.text_processor import (
    TextProcessor,
)

from app.services.evaluation.feature_extractors.text.statistics_feature_extractor import (
    StatisticsFeatureExtractor,
)


def test_statistics_feature_extractor():

    answers = [
        "Hello, my name is Aditya. I know Python and FastAPI.",

        "I built ResumeGuide using Docker PostgreSQL and AWS.",

        "I enjoy solving machine learning problems.",
    ]

    text_processor = TextProcessor()
    documents = [
        text_processor.process(answer)
        for answer in answers
    ]

    result = StatisticsFeatureExtractor.extract(
        documents=documents,
        answer_durations=[20, 40, 30],
    )

    assert result["total_answers"] == 3

    assert result["total_words"] > 0

    assert result["unique_words"] > 0

    assert result["average_words_per_answer"] > 0

    assert result["average_word_length"] > 0

    assert result["average_sentence_length"] > 0

    assert result["average_answer_duration"] == 30

    assert result["empty_answers"] == 0