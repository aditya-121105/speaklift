# backend/app/ai/nlp/processors/__init__.py
"""
NLP Processors
==============

Core NLP processing components that run a DocumentContent through the
linguistic analysis pipeline.

Sprint C.4.1 — SpacyProcessor and Normalizer implemented.
"""

from .spacy_processor import SpacyProcessor
from .normalizer import Normalizer

__all__ = [
    "SpacyProcessor",
    "Normalizer",
]
