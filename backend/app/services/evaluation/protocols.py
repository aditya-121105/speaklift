from typing import Protocol
from app.schemas.evaluation.text_document import TextDocument

class TextProcessorProtocol(Protocol):
    def process(self, text: str) -> TextDocument:
        ...

class VocabularyExtractorProtocol(Protocol):
    def extract(self, documents: list[TextDocument]) -> dict[str, float | int]:
        ...
