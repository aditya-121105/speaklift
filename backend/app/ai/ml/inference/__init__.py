# backend/app/ai/ml/inference/__init__.py
"""
ML Inference
============

Prediction runners. Accept preprocessed feature vectors (from
ml/preprocessing/) and a loaded model (from ml/models/), and return
typed prediction objects.

Design rules
------------
- Inference runners are STATELESS. Models are injected, not stored.
- Inference must be synchronous (no asyncio in ML inference paths).
- Each runner produces a typed output schema, not a raw numpy array.
- Errors are raised as AIProcessingError (from ai/shared/exceptions.py).

Sprint C.2 — package skeleton only.
"""
