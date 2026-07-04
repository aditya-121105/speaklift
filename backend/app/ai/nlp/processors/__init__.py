# backend/app/ai/nlp/processors/__init__.py
"""
NLP Processors
==============

Core NLP processing components that run a DocumentContent through the
linguistic analysis pipeline.

Planned processors
------------------
SpacyProcessor  (Sprint C.3)
    - Tokenisation, POS tagging, dependency parsing
    - Named Entity Recognition (PERSON, ORG, GPE, DATE, etc.)
    - Sentence boundary detection
    - Lemmatisation and stop-word detection

NLTKProcessor   (Sprint C.4)
    - Fallback tokenisation for languages/domains not covered by spaCy
    - Word frequency analysis

Design contract
---------------
Processors are stateless transformers: DocumentContent → ProcessedDocument.
They load NLP models via the resource managers in nlp/resources/.
They must NOT be instantiated with model weights — models are injected or
retrieved via singleton managers.

Sprint C.2 — package skeleton only.
"""
