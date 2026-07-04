# backend/app/ai/__init__.py
"""
SpeakLift AI Core Infrastructure
=================================

This package is the exclusive home for all AI and ML logic in SpeakLift.

Architecture rule
-----------------
AI logic MUST live here. It must NOT be scattered across services/, core/,
or endpoints/. Business services in app/services/ may call into this package,
but no AI implementation may live inside services/.

Sub-packages
------------
shared/            — Cross-cutting AI types, exceptions, and constants
document_processing/ — Document loading, cleaning, and extraction interfaces
nlp/               — Natural Language Processing pipeline (spaCy, NLTK)
ml/                — Classical Machine Learning models and inference
embeddings/        — Sentence Transformers and vector operations
llm/               — Large Language Model provider abstraction
evaluation/        — Answer quality scoring and analysis
recommendations/   — Personalised learning recommendations
ranking/           — Candidate / question ranking algorithms
utils/             — Shared AI utilities

Sprint history
--------------
C.2 (2026-07-03) — Package skeleton created. Abstract interfaces defined.
                   No implementations yet.
"""
