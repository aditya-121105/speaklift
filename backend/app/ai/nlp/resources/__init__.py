# backend/app/ai/nlp/resources/__init__.py
"""
NLP Resources
=============

Resource managers for NLP models and external data.

Sprint C.4.1 — SpacyResourceManager and JSON taxonomies implemented.
"""

from .spacy_resource import SpacyResourceManager
from .taxonomy_resource import TaxonomyResourceManager

__all__ = [
    "SpacyResourceManager",
    "TaxonomyResourceManager",
]
