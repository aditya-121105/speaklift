# backend/app/ai/ml/preprocessing/__init__.py
"""
ML Preprocessing
================

Feature engineering: transforms structured NLP output (ExtractedEntities,
SkillSet, ExperienceRecord) into numeric feature vectors for ML models.

Design rules
------------
- Preprocessing code is SHARED between training and inference pipelines.
  This is the only way to prevent training-serving skew.
- Preprocessors are STATELESS FUNCTIONS or STATELESS CLASSES.
  State (e.g. fitted scalers, vocabularies) is loaded from artefacts,
  not built at request time.
- Each preprocessor produces a typed FeatureVector class, not a raw list.

Sprint C.2 — package skeleton only.
"""
