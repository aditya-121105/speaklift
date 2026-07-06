"""
JD Extractors Package.
Currently contains only the base registry wiring for future JD extractors.
"""
from app.ai.nlp.extractors.base import ExtractorRegistry
from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities

def get_jd_extractor_registry() -> ExtractorRegistry:
    """
    Returns a configured ExtractorRegistry for JD extraction.
    Currently empty, extractors will be registered here in upcoming sprints.
    """
    registry = ExtractorRegistry(schema_cls=ExtractedJDEntities)
    return registry

__all__ = ["get_jd_extractor_registry"]
