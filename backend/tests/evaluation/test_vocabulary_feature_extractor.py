from app.services.evaluation.feature_extractors.text.text_processor import (
    TextProcessor,
)

from app.services.evaluation.feature_extractors.text.vocabulary_feature_extractor import (
    VocabularyFeatureExtractor,
)

text_processor = TextProcessor()
vocab_extractor = VocabularyFeatureExtractor()

documents = [
    text_processor.process(
        "I developed AI applications using Python and FastAPI."
    ),
    text_processor.process(
        "I deployed Docker containers on AWS."
    ),
]

features = vocab_extractor.extract(documents)

print(features)