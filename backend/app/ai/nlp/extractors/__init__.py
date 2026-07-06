# backend/app/ai/nlp/extractors/__init__.py
"""
NLP Extractors
==============

Domain-specific entity extractors for resume and job description parsing.

Each extractor receives processed NLP output and returns a typed,
structured result for a specific information category.

Sprint C.4.2 — Base infrastructure (EntityExtractor, ExtractorRegistry) implemented.
"""

from .base import EntityExtractor, ExtractorRegistry

__all__ = [
    "EntityExtractor",
    "ExtractorRegistry",
]
