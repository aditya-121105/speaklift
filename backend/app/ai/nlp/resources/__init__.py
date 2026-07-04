# backend/app/ai/nlp/resources/__init__.py
"""
NLP Resources
=============

Resource managers for NLP models and external data.

Responsibilities
----------------
- Load and cache spaCy models (currently: en_core_web_sm in app/core/nlp.py)
- Download and manage NLTK corpora on first use
- Load custom vocabulary files (skills taxonomy, technology lists)
- Provide singleton access to all NLP resources

Migration plan (Sprint C.3)
----------------------------
The existing spaCy singleton in app/core/nlp.py should be migrated here
as SpacyResourceManager. This centralises all NLP model lifecycle management
inside app/ai/ where it belongs architecturally.

Sprint C.2 — package skeleton only. app/core/nlp.py remains in place.
"""
