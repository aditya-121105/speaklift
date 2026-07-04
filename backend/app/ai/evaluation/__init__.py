# backend/app/ai/evaluation/__init__.py
"""
AI Evaluation
=============

Responsible for AI-driven answer quality assessment.

Architecture position
---------------------
Candidate Answer (text)
    │
    ├──▶ NLP Feature Extraction  (app/ai/nlp/)
    │        — vocabulary richness, grammar, fluency, readability
    │
    ├──▶ Embedding Similarity     (app/ai/embeddings/)
    │        — semantic closeness to model/expected answer
    │
    └──▶ ML Scoring               (app/ai/ml/)
             — weighted composite quality score

This sub-package orchestrates the above pipelines into a single
EvaluationPipeline that produces a typed EvaluationResult.

Relationship to app/services/evaluation/
-----------------------------------------
The current evaluation feature extractors live in:
  app/services/evaluation/feature_extractors/

Those are DOMAIN-SPECIFIC feature extractors for the interview evaluation
business domain. They will call into app/ai/ for raw NLP and embedding
primitives, but remain in services/ as business logic coordinators.

This app/ai/evaluation/ sub-package will house GENERIC AI evaluation
utilities — reusable scoring components that are not tied to the
interview domain. The business-specific orchestration stays in services/.

Planned components
------------------
EvaluationPipeline    (Sprint C.5)
    — Chains NLP extraction → embedding similarity → ML scoring.
    — Returns EvaluationResult with per-dimension scores.

TextQualityScorer     (Sprint C.5)
    — Rule-based + ML scoring of text quality (fluency, grammar, etc.)
    — Wraps the existing StatisticsFeatureExtractor and VocabularyFeatureExtractor.

SemanticSimilarityScorer (Sprint C.5)
    — Embedding-based relevance scoring.

Sprint C.2 — skeleton only.
Sprint C.5 — implement EvaluationPipeline and scorers.
"""
