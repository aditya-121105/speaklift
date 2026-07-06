import pytest
from app.ai.document_processing.schemas import DocumentContent
from app.ai.nlp.processors.spacy_processor import SpacyProcessor
from app.ai.nlp.processors.normalizer import Normalizer
from app.ai.nlp.extractors.contact_extractor import ContactExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext


def test_contact_extractor_realistic_resume():
    raw_text = """
    Jane Doe
    Software Engineer
    Email: jane.doe@example.com | Phone: +1-555-555-0199 | Location: Seattle, WA
    LinkedIn: linkedin.com/in/janedoe
    GitHub: github.com/janedoe
    Kaggle: kaggle.com/janedoe
    LeetCode: leetcode.com/janedoe
    HackerRank: hackerrank.com/janedoe
    Portfolio: janedoe.dev
    """

    doc = DocumentContent(
        raw_text=raw_text,
        cleaned_text=raw_text,
        source_filename="jane_doe_resume.pdf"
    )

    processor = SpacyProcessor()
    processed = processor.process(doc.cleaned_text)
    
    normalizer = Normalizer()
    normalized_text = normalizer.normalize(processed)

    context = ProcessingContext(
        document=doc,
        processed_document=processed,
        normalized_text=normalized_text,
        metadata={},
        config={}
    )

    extractor = ContactExtractor()
    contact_info = extractor.extract(context)

    # Name might be extracted via PERSON entity or first line title case
    assert contact_info.full_name == "Jane Doe"
    assert contact_info.email == "jane.doe@example.com"
    assert contact_info.phone == "+1-555-555-0199"
    assert "Seattle" in contact_info.location
    assert "linkedin.com/in/janedoe" in contact_info.linkedin_url
    assert "github.com/janedoe" in contact_info.github_url
    assert "kaggle.com/janedoe" in contact_info.kaggle_url
    assert "leetcode.com/janedoe" in contact_info.leetcode_url
    assert "hackerrank.com/janedoe" in contact_info.hackerrank_url
    assert "janedoe.dev" in contact_info.portfolio_url


def test_contact_extractor_minimal():
    raw_text = "John Smith\nEmail: john@gmail.com"
    doc = DocumentContent(
        raw_text=raw_text,
        cleaned_text=raw_text,
        source_filename="minimal.pdf"
    )
    processor = SpacyProcessor()
    processed = processor.process(doc.cleaned_text)
    context = ProcessingContext(
        document=doc,
        processed_document=processed,
        normalized_text=raw_text,
        metadata={},
        config={}
    )
    extractor = ContactExtractor()
    contact_info = extractor.extract(context)

    assert contact_info.full_name == "John Smith"
    assert contact_info.email == "john@gmail.com"
    assert contact_info.phone is None
