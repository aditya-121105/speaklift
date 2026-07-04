# backend/app/ai/nlp/schemas/__init__.py
"""
NLP Schemas
===========

Pydantic models for NLP pipeline inputs and outputs.

These schemas decouple the NLP pipeline from downstream consumers
(ML, embeddings, business services). Downstream components depend on
these schemas, not on spaCy or NLTK internal types.

Planned schemas
---------------
ProcessedDocument   — output of SpacyProcessor (sentences, tokens, entities)
ExtractedEntities   — aggregate of all entity extraction results
SkillSet            — structured skill extraction output
EducationRecord     — structured education extraction output
ExperienceRecord    — structured work experience extraction output
ProjectRecord       — structured project extraction output

Sprint C.2 — package skeleton only.
"""
