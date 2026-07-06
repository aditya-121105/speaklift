import time
from pydantic import BaseModel
from app.ai.document_processing.schemas import DocumentContent
from app.ai.nlp.processors.spacy_processor import SpacyProcessor
from app.ai.nlp.processors.normalizer import Normalizer
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.schemas.contact_schema import ContactInfo
from app.ai.nlp.schemas.skill_schema import SkillSet
from app.ai.nlp.extractors.base import ExtractorRegistry


class NLPPipeline:
    """
    Orchestrates the NLP extraction process:
    DocumentContent -> spaCy -> Normalization -> Plugins -> ExtractedEntities
    """

    def __init__(
        self,
        processor: SpacyProcessor,
        normalizer: Normalizer,
        registry: ExtractorRegistry,
    ) -> None:
        self._processor = processor
        self._normalizer = normalizer
        self._registry = registry

    def run(self, document: DocumentContent) -> BaseModel:
        """
        Execute the NLP pipeline on the given document.
        """
        start_time = time.time()

        # 1. Process via spaCy
        processed = self._processor.process(document.cleaned_text)

        # 2. Normalize
        normalized_text = self._normalizer.normalize(processed)

        # 3. Assemble ProcessingContext
        context = ProcessingContext(
            document=document,
            processed_document=processed,
            normalized_text=normalized_text,
            metadata={},
            config={}
        )

        # 4. Extract entities via registered plugins
        extracted_kwargs = {}
        for extractor in self._registry.get_all():
            extracted_kwargs[extractor.domain] = extractor.extract(context)

        # 5. Build Final Output
        processing_time_ms = int((time.time() - start_time) * 1000)

        schema_cls = getattr(self._registry, "schema_cls", ExtractedEntities)
        if schema_cls.__name__ == "ExtractedJDEntities":
            # Provide defaults for non-list complex objects in JD
            from app.ai.nlp.schemas.jd.jd_employment_schema import JDEmploymentRecord
            from app.ai.nlp.schemas.jd.jd_company_schema import JDCompanyRecord
            return schema_cls(
                employment=extracted_kwargs.get("employment", JDEmploymentRecord(
                    job_title=None, location=None, remote_type=None, salary=None, confidence=0.0
                )),
                skills=extracted_kwargs.get("skills", []),
                experience=extracted_kwargs.get("experience", []),
                education=extracted_kwargs.get("education", []),
                responsibilities=extracted_kwargs.get("responsibilities", []),
                company=extracted_kwargs.get("company", JDCompanyRecord(
                    company_name=None, industry=None, company_size=None,
                    culture_keywords=None, website=None, confidence=0.0
                )),
                source_filename=document.source_filename,
                pipeline_version="C.5.2",
                processing_time_ms=processing_time_ms,
                document_language="en",
                model_version="en_core_web_sm"
            )

        return ExtractedEntities(
            contact=extracted_kwargs.get("contact", ContactInfo(
                full_name=None, email=None, phone=None, location=None,
                linkedin_url=None, github_url=None, portfolio_url=None,
                leetcode_url=None, hackerrank_url=None, kaggle_url=None
            )),
            skills=extracted_kwargs.get("skills", SkillSet(skills=[], technologies=[])),
            education=extracted_kwargs.get("education", []),
            experience=extracted_kwargs.get("experience", []),
            projects=extracted_kwargs.get("projects", []),
            certifications=extracted_kwargs.get("certifications", []),
            source_filename=document.source_filename,
            pipeline_version="C.4.2",
            processing_time_ms=processing_time_ms,
            document_language="en",
            model_version="en_core_web_sm"
        )
