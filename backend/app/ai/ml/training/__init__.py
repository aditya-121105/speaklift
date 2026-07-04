# backend/app/ai/ml/training/__init__.py
"""
ML Training
===========

Offline training pipelines. These are NOT called from the web server.
They are invoked from backend/scripts/ during model development and
retraining cycles.

Design rules
------------
- Training code is NEVER imported by web server modules.
- Training pipelines use the same preprocessing/ code used in inference.
  This guarantees train/serve consistency (no training-serving skew).
- Trained model artefacts are serialised and stored in a models/ directory
  outside the application package (configured via settings).

Sprint C.2 — package skeleton only.
"""
