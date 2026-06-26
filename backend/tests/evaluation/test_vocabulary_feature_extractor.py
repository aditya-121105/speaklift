from app.services.evaluation.feature_extractors.text.text_processor import (
    TextProcessor,
)

from app.services.evaluation.feature_extractors.text.vocabulary_feature_extractor import (
    VocabularyFeatureExtractor,
)

documents = [
    TextProcessor.process(
        "I developed AI applications using Python and FastAPI."
    ),
    TextProcessor.process(
        "I deployed Docker containers on AWS."
    ),
]

features = VocabularyFeatureExtractor.extract(documents)

print(features)