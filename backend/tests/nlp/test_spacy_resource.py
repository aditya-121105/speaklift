from app.ai.nlp.resources.spacy_resource import SpacyResourceManager


def test_spacy_resource_manager_singleton():
    model1 = SpacyResourceManager.get_model()
    model2 = SpacyResourceManager.get_model()
    
    assert model1 is model2
    assert SpacyResourceManager.is_loaded()
