"""
==============================================================================
Module:
    Text Document

Sprint:
    Sprint 4 - Evaluation Engine

Purpose:
    Serializable representation of one processed interview answer.

Produced By:
    TextProcessor

Consumed By:
    - StatisticsFeatureExtractor
    - VocabularyFeatureExtractor
    - KeywordFeatureExtractor
    - ReadabilityFeatureExtractor
    - GrammarFeatureExtractor
    - SentimentFeatureExtractor
    - SemanticFeatureExtractor

NOTE:
    This schema intentionally does NOT expose spaCy objects.
    Only derived information required by downstream modules.

==============================================================================
"""

from pydantic import BaseModel, Field


class TextDocument(BaseModel):
    """
    Processed representation of one interview answer.
    """

    original_text: str = Field(
        description="Original interview answer."
    )

    normalized_text: str = Field(
        description="Normalized lowercase text."
    )

    tokens: list[str] = Field(
        default_factory=list,
        description="Alphabetic tokens."
    )

    lemmas: list[str] = Field(
        default_factory=list,
        description="Base form of each token."
    )

    sentences: list[str] = Field(
        default_factory=list,
        description="Detected sentences."
    )

    named_entities: list[str] = Field(
        default_factory=list,
        description="Named entities detected by spaCy."
    )

    stop_words: list[str] = Field(
        default_factory=list,
        description="Stop words detected by spaCy."
    )

    content_words: list[str] = Field(
        default_factory=list,
        description=(
            "Content words (nouns, verbs, adjectives, adverbs)."
        )
    )