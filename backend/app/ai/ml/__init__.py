# backend/app/ai/ml/__init__.py
"""
ML — Classical Machine Learning
=================================

Responsible for classical ML models: training, inference, and preprocessing.

Architecture position
---------------------
NLP Extractors (structured data)
    │
    ▼
ML Preprocessing + Feature Engineering
    │
    ▼
ML Model Inference
    │
    ▼
Scores / Rankings (consumed by business services)

Sub-packages
------------
models/        — Model definitions and serialisation contracts.
                 Each model class wraps a scikit-learn or XGBoost estimator
                 behind a stable interface.

inference/     — Prediction runners. Accept preprocessed feature vectors,
                 return typed prediction objects.

training/      — Offline training pipelines (not part of the web server).
                 Called from scripts/, not from the API.

preprocessing/ — Feature engineering and data preparation.
                 Transforms structured NLP output into numeric feature vectors.

Planned models
--------------
ResumeQualityModel   (Sprint C.4) — Score resume quality from 0–100
CandidateRankModel   (Sprint C.5) — Rank candidates against a job description
RecommendationModel  (Sprint C.5) — Suggest improvement areas

Engineering philosophy
----------------------
Follow the Complexity Gradient Principle: try rule-based → ML → DL.
ML is justified here because scoring requires generalisation across
diverse resume formats and domains.

Sprint C.2 — package skeleton only. No models.
"""
