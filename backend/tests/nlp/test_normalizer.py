import pytest
from app.ai.nlp.processors.normalizer import Normalizer
from app.ai.nlp.schemas.processed_document import ProcessedDocument


def test_normalizer_synonyms():
    normalizer = Normalizer()
    
    # Create a dummy processed document
    processed = ProcessedDocument(
        original_text="I use NodeJS, ReactJS, and Postgres for backend.",
        tokens=[],
        lemmas=[],
        sentences=[],
        named_entities=[],
        noun_chunks=[],
        pos_tags=[]
    )
    
    normalized_text = normalizer.normalize(processed)
    
    assert "node.js" in normalized_text.lower()
    assert "react" in normalized_text.lower()
    assert "postgresql" in normalized_text.lower()
    assert "NodeJS" not in normalized_text
    assert "ReactJS" not in normalized_text
