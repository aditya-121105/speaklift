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

import spacy


class NLPResourceManager:

    """
    Singleton-style manager responsible for
    loading NLP resources only once.
    """

    _spacy_model = None

    @classmethod
    def get_spacy_model(cls):
        """
        Return the shared spaCy model.
        """

        if cls._spacy_model is None:

            cls._spacy_model = spacy.load(
                "en_core_web_sm"
            )

        return cls._spacy_model