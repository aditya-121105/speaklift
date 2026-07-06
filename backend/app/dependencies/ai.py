from app.ai.document_processing.services import DocumentExtractionService
from app.ai.document_processing.services.document_extraction_service import build_default_extraction_service
from app.ai.nlp.pipeline import NLPPipeline
from app.ai.nlp.processors.spacy_processor import SpacyProcessor
from app.ai.nlp.processors.normalizer import Normalizer
from app.ai.nlp.extractors.base import ExtractorRegistry
from app.ai.nlp.extractors.contact_extractor import ContactExtractor
from app.ai.nlp.extractors.skill_extractor import SkillExtractor
from app.ai.nlp.extractors.education_extractor import EducationExtractor
from app.ai.nlp.extractors.experience_extractor import ExperienceExtractor
from app.ai.nlp.extractors.project_extractor import ProjectExtractor
from app.ai.nlp.extractors.certification_extractor import CertificationExtractor
from app.ai.nlp.validators.entity_validator import EntityValidator
from app.services.candidate_profile.builder import CandidateProfileBuilder


def get_document_extractor() -> DocumentExtractionService:
    return build_default_extraction_service()


def get_nlp_pipeline() -> NLPPipeline:
    registry = ExtractorRegistry()
    registry.register(ContactExtractor())
    registry.register(SkillExtractor())
    registry.register(EducationExtractor())
    registry.register(ExperienceExtractor())
    registry.register(ProjectExtractor())
    registry.register(CertificationExtractor())
    
    return NLPPipeline(
        processor=SpacyProcessor(),
        normalizer=Normalizer(),
        registry=registry
    )


def get_entity_validator() -> EntityValidator:
    return EntityValidator()


def get_profile_builder() -> CandidateProfileBuilder:
    return CandidateProfileBuilder()
