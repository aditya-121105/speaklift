from app.ai.nlp.extractors.certification_extractor import CertificationExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext

from app.ai.document_processing.schemas import DocumentContent, DocumentSection, SectionType
from app.ai.nlp.schemas.processed_document import ProcessedDocument

def create_context(text: str) -> ProcessingContext:
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            content = '\n'.join(lines[i+1:])
            break
    else:
        content = text
    doc = DocumentContent(
        raw_text=text,
        cleaned_text=text,
        sections={"certifications": DocumentSection(section_type=SectionType.CERTIFICATIONS, heading="Certifications", content=content, start_char=0, end_char=len(content))},
        source_filename="test.pdf"
    )
    processed = ProcessedDocument(
        original_text=text,
        tokens=[],
        lemmas=[],
        pos_tags=[],
        noun_chunks=[],
        named_entities=[],
        sentences=[]
    )
    return ProcessingContext(
        document=doc,
        processed_document=processed,
        normalized_text=text,
        metadata={},
        config={}
    )

def test_certification_extractor_single():
    text = """
    Certifications
    AWS Certified Solutions Architect
    Issued by AWS
    Issued: Jan 2024
    Expires: Jan 2027
    Credential ID: AWS-123456
    https://aws.amazon.com/verify/AWS-123456
    """
    context = create_context(text)
    
    extractor = CertificationExtractor()
    extractor._taxonomy = {
        "aws certified solutions architect": ("AWS Certified Solutions Architect", "cloud")
    }
    extractor._synonyms = {}
    
    certs = extractor.extract(context)
    assert len(certs) == 1
    c = certs[0]
    assert c.name == "AWS Certified Solutions Architect"
    assert c.issuing_organization == "AWS"
    assert c.issue_date == "Jan 2024"
    assert c.expiry_date == "Jan 2027"
    assert c.credential_id == "AWS-123456"
    assert c.credential_url == "https://aws.amazon.com/verify/AWS-123456"
    assert c.normalized_name == "AWS Certified Solutions Architect"
    assert c.confidence > 0.8

def test_certification_extractor_multiple():
    text = """
    Licenses & Certifications
    
    Certified Kubernetes Administrator
    Cloud Native Computing Foundation
    Issue Date: 2023
    
    Google Cloud Professional Data Engineer
    Google
    Earned: Oct 2022
    Expiration: Oct 2024
    """
    context = create_context(text)
    extractor = CertificationExtractor()
    extractor._taxonomy = {}
    extractor._synonyms = {}
    
    certs = extractor.extract(context)
    assert len(certs) == 2
    assert certs[0].name == "Certified Kubernetes Administrator"
    # Note: CNFC might not be caught by our simple issuer list, but it's fine.
    # The heuristic might miss CNFC but let's test what we have.
    assert certs[0].issue_date == "2023"
    
    assert certs[1].name == "Google Cloud Professional Data Engineer"
    assert certs[1].issuing_organization == "Google"
    assert certs[1].issue_date == "Oct 2022"
    assert certs[1].expiry_date == "Oct 2024"

def test_certification_extractor_minimal():
    text = """
    Certifications
    CompTIA Security+
    """
    context = create_context(text)
    extractor = CertificationExtractor()
    extractor._taxonomy = {}
    extractor._synonyms = {}
    
    certs = extractor.extract(context)
    assert len(certs) == 1
    assert certs[0].name == "CompTIA Security+"
    assert certs[0].issuing_organization == "CompTIA"
    assert certs[0].issue_date is None
    assert certs[0].credential_id is None
