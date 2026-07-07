"""
JD Extractors Package.
Currently contains only the base registry wiring for future JD extractors.
"""
from app.ai.nlp.extractors.base import ExtractorRegistry
from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities
from app.ai.nlp.extractors.jd.jd_skill_extractor import JDSkillExtractor

def get_jd_extractor_registry() -> ExtractorRegistry:
    """
    Returns a configured ExtractorRegistry for JD extraction.
    Currently registers:
    - JDSkillExtractor
    """
    registry = ExtractorRegistry(schema_cls=ExtractedJDEntities)
    registry.register(JDSkillExtractor())
    return registry

__all__ = ["get_jd_extractor_registry"]
