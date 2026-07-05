from typing import Any
from pydantic import BaseModel, ConfigDict
from app.ai.document_processing.schemas import DocumentContent
from app.ai.nlp.schemas.processed_document import ProcessedDocument


class ProcessingContext(BaseModel):
    """
    Immutable parameter object passed to all EntityExtractors.
    Contains everything needed to extract domain entities.
    """
    model_config = ConfigDict(frozen=True)

    document: DocumentContent
    processed_document: ProcessedDocument
    normalized_text: str
    metadata: dict[str, Any]
    config: dict[str, Any]
