from pydantic import BaseModel, ConfigDict


class NamedEntity(BaseModel):
    """
    A named entity extracted by the NLP processor.
    """
    model_config = ConfigDict(frozen=True)

    text: str
    label: str  # spaCy label: PERSON, ORG, GPE, DATE, CARDINAL, etc.
    start_char: int
    end_char: int


class ProcessedDocument(BaseModel):
    """
    Output of SpacyProcessor.
    Serialisable, completely decoupled from spaCy types.
    """
    model_config = ConfigDict(frozen=True)

    original_text: str
    tokens: list[str]  # alphabetic tokens, lowercased
    lemmas: list[str]  # lemmatised alphabetic tokens
    sentences: list[str]  # sentence boundary text
    named_entities: list[NamedEntity]
    noun_chunks: list[str]  # NP chunk texts (crucial for skill/project detection)
    pos_tags: list[tuple[str, str]]  # [(token, POS_tag), ...]
