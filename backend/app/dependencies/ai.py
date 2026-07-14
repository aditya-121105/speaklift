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

from app.ai.nlp.extractors.jd import get_jd_extractor_registry
from app.ai.nlp.validators.duplicate import DuplicateValidator
from app.ai.nlp.validators.salary_range import SalaryRangeValidator
from app.ai.nlp.validators.experience_range import ExperienceRangeValidator
from app.services.job_profile.builder import JobProfileBuilder


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


def get_jd_nlp_pipeline() -> NLPPipeline:
    return NLPPipeline(
        processor=SpacyProcessor(),
        normalizer=Normalizer(),
        registry=get_jd_extractor_registry()
    )


def get_jd_entity_validator() -> EntityValidator:
    return EntityValidator(
        validators=[
            DuplicateValidator(),
            SalaryRangeValidator(),
            ExperienceRangeValidator(),
        ]
    )


def get_job_profile_builder() -> JobProfileBuilder:
    return JobProfileBuilder()
