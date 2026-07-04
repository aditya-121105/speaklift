# backend/app/ai/ml/models/__init__.py
"""
ML Model Definitions
====================

Model wrapper classes. Each class encapsulates a trained estimator
behind a stable, versioned interface.

Design rules
------------
- Model classes are PURE DATA CONTAINERS + INTERFACE DEFINITIONS.
- No training logic in this package (that belongs in ml/training/).
- No preprocessing (that belongs in ml/preprocessing/).
- Each model class implements a common abstract interface so inference
  runners in ml/inference/ can treat all models uniformly.

Planned models
--------------
ResumeQualityModel    (Sprint C.4)
    Inputs : ResumeFeatureVector (from ml/preprocessing/)
    Outputs: ResumeQualityScore (0–100 + confidence)

CandidateRankModel    (Sprint C.5)
    Inputs : CandidateFeatureVector, JobFeatureVector
    Outputs: RankScore (float) + feature importance breakdown

Sprint C.2 — package skeleton only.
"""
