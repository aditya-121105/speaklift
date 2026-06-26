"""
==============================================================================
Module:
    Text Feature Vector

Sprint:
    Sprint 4 - Evaluation Engine

Purpose:
    Represents structured numerical and statistical features extracted
    from a candidate's text answers.

Architecture:

Interview Answers
        │
        ▼
Text Feature Extractor
        │
        ▼
TextFeatureVector
        │
        ▼
Feature Fusion Service
        │
        ▼
InterviewFeatureVector

Responsibilities:
    ✔ Store deterministic text features
    ✔ Provide ML-ready structured data
    ✔ Remain independent of evaluation logic

Does NOT:
    ✘ Calculate scores
    ✘ Call AI APIs
    ✘ Access the database
    ✘ Generate recommendations

Future Upgrades:
    - Grammar statistics
    - Readability metrics
    - TF-IDF features
    - Sentence embeddings
    - Named Entity Recognition
    - Semantic similarity

==============================================================================
Interview Notes

Q1. Why use Feature Vectors?

Answer:
Machine Learning models operate on numerical
representations rather than raw text.

A Feature Vector transforms unstructured interview
answers into structured data that can be consumed by
Rule Engines, ML models, DL models and LLM pipelines.

Q2. Why is this a Pydantic model?

Answer:
This is a Data Transfer Object (DTO).

It provides:

- Validation
- Type safety
- Serialization
- Clean communication between services

==============================================================================
Engineering Notes

This schema contains only extracted features.

Business logic belongs inside Feature Extractors.

Evaluation logic belongs inside Evaluators.

==============================================================================
"""

from pydantic import (
    BaseModel,
    Field,
)


class TextFeatureVector(BaseModel):
    """
    Structured text features extracted from
    interview answers.
    """

    # ==========================================================
    # Basic Statistics
    # ==========================================================

    total_answers: int = Field(
        description="Total interview answers.",
        ge=0,
    )

    total_words: int = Field(
        description="Total words across all answers.",
        ge=0,
    )

    unique_words: int = Field(
        description="Unique words used.",
        ge=0,
    )

    average_words_per_answer: float = Field(
        description="Average words per answer.",
        ge=0,
    )

    average_word_length: float = Field(
        description="Average word length.",
        ge=0,
    )

    average_sentence_length: float = Field(
        description="Average sentence length in words.",
        ge=0,
    )

    vocabulary_richness: float = Field(
        description=(
            "Unique words divided by total words."
        ),
        ge=0,
        le=1,
    )

    # ==========================================================
    # Response Quality
    # ==========================================================

    empty_answers: int = Field(
        ge=0,
    )

    short_answers: int = Field(
        ge=0,
    )

    long_answers: int = Field(
        ge=0,
    )

    average_answer_duration: float = Field(
        ge=0,
    )

    # ==========================================================
    # Keyword Features
    # ==========================================================

    technical_keyword_count: int = Field(
        ge=0,
    )

    behavioral_keyword_count: int = Field(
        ge=0,
    )

    # ==========================================================
    # Readability Features
    # ==========================================================

    average_paragraphs_per_answer: float = Field(
        ge=0,
    )

    average_sentences_per_answer: float = Field(
        ge=0,
    )

    # ==========================================================
    # Grammar Features
    # ==========================================================

    grammar_error_count: int = Field(
        ge=0,
    )

    spelling_error_count: int = Field(
        ge=0,
    )

    # ==========================================================
    # Future NLP Features
    # ==========================================================

    sentiment_score: float | None = Field(
        default=None,
        description=(
            "Reserved for sentiment analysis."
        ),
    )

    readability_score: float | None = Field(
        default=None,
        description=(
            "Reserved for readability algorithms."
        ),
    )

    semantic_similarity_score: float | None = Field(
        default=None,
        description=(
            "Reserved for transformer embeddings."
        ),
    )