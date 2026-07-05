import pytest
from app.ai.nlp.resources.spacy_resource import SpacyResourceManager
from app.ai.nlp.processors.spacy_processor import SpacyProcessor


def test_spacy_processor():
    processor = SpacyProcessor()
    text = "John Doe works at Google in New York."
    
    result = processor.process(text)
    
    assert result.original_text == text
    assert "john" in result.tokens
    assert "doe" in result.tokens
    assert "works" in result.tokens
    
    # Check NER
    entity_labels = [ent.label for ent in result.named_entities]
    assert "PERSON" in entity_labels  # John Doe
    assert "ORG" in entity_labels     # Google
    assert "GPE" in entity_labels     # New York

    # Check sentences
    assert len(result.sentences) == 1
    assert result.sentences[0] == text

    # Check noun chunks (at least some NP should be extracted)
    assert len(result.noun_chunks) > 0
