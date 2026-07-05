"""
==============================================================================
Module:
    NLP Resource Manager

Sprint:
    Sprint 4 - Evaluation Engine

Purpose:
    Centralized loader for Natural Language Processing resources.

Architecture:

                NLP Resource Manager
                        │
        ┌───────────────┼────────────────┐
        │               │                │
      spaCy      LanguageTool     SentenceTransformer
        │
        ▼
Feature Extractors
        │
        ▼
Evaluation Pipeline

Responsibilities:
    ✔ Load NLP models once
    ✔ Share models across the application
    ✔ Avoid repeated initialization
    ✔ Reduce memory consumption

Does NOT:
    ✘ Perform feature extraction
    ✘ Evaluate interviews
    ✘ Access database

==============================================================================
Interview Notes

Q. Why use a central NLP manager?

Answer:

Many NLP models are expensive to load.

Loading them repeatedly:

- increases startup time
- wastes memory
- reduces throughput

A shared resource manager loads models once and allows
the rest of the application to reuse them.

This pattern is common in production AI systems.

==============================================================================
"""

# Deprecation shim: redirect to the new NLP architecture
from app.ai.nlp.resources.spacy_resource import SpacyResourceManager


class NLPResourceManager:
    """
    Adapter to maintain backward compatibility for the evaluation pipeline
    while it transitions to the new NLP architecture.
    """
    @classmethod
    def get_spacy_model(cls):
        """
        Legacy method signature. Delegates to the new resource manager.
        """
        return SpacyResourceManager.get_model()