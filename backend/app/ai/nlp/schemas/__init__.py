# backend/app/ai/nlp/schemas/__init__.py
"""
NLP Schemas
===========

Pydantic models for NLP pipeline inputs and outputs.

These schemas decouple the NLP pipeline from downstream consumers
(ML, embeddings, business services). Downstream components depend on
these schemas, not on spaCy or NLTK internal types.

Sprint C.4.1 — schemas implemented.
"""

from .processed_document import ProcessedDocument, NamedEntity
from .processing_context import ProcessingContext
from .skill_schema import SkillEntry, SkillSet
from .education_schema import EducationRecord
from .experience_schema import ExperienceRecord
from .project_schema import ProjectRecord
from .certification_schema import CertificationRecord
from .contact_schema import ContactInfo
from .extracted_entities import ExtractedEntities

__all__ = [
    "ProcessedDocument",
    "NamedEntity",
    "ProcessingContext",
    "SkillEntry",
    "SkillSet",
    "EducationRecord",
    "ExperienceRecord",
    "ProjectRecord",
    "CertificationRecord",
    "ContactInfo",
    "ExtractedEntities",
]
