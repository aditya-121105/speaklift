# backend/app/ai/nlp/extractors/__init__.py
"""
NLP Extractors
==============

Domain-specific entity extractors for resume and job description parsing.

Each extractor receives processed NLP output and returns a typed,
structured result for a specific information category.

Sprint C.4.3 — ContactExtractor and SkillExtractor implemented.
"""

from .base import EntityExtractor, ExtractorRegistry
from .contact_extractor import ContactExtractor
from .skill_extractor import SkillExtractor

__all__ = [
    "EntityExtractor",
    "ExtractorRegistry",
    "ContactExtractor",
    "SkillExtractor",
]

