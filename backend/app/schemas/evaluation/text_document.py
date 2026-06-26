"""
==============================================================================
Module:
    Text Document

Purpose:
    Serializable representation of a processed interview answer.

This schema is produced only by TextProcessor and consumed by
all feature extractors.

NOTE:
    This schema intentionally does NOT expose spaCy objects.
    Only extracted information is stored.
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
        description="Base forms of words."
    )

    sentences: list[str] = Field(
        default_factory=list,
        description="Sentence segmentation."
    )

    named_entities: list[str] = Field(
        default_factory=list,
        description="Named entities detected by spaCy."
    )