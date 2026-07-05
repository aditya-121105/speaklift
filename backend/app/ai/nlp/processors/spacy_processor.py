from app.ai.nlp.resources.spacy_resource import SpacyResourceManager
from app.ai.nlp.schemas.processed_document import ProcessedDocument, NamedEntity


class SpacyProcessor:
    """
    Runs text through the spaCy pipeline once per document.
    Returns ProcessedDocument — a pure-Pydantic, spaCy-free output.
    """

    def __init__(self, resource_manager: type[SpacyResourceManager] = SpacyResourceManager) -> None:
        self._resource_manager = resource_manager

    def process(self, text: str) -> ProcessedDocument:
        """
        Process the text and extract linguistic features.
        """
        nlp = self._resource_manager.get_model()
        doc = nlp(text)

        tokens = []
        lemmas = []
        pos_tags = []

        for token in doc:
            if token.is_alpha:
                tokens.append(token.text.lower())
                lemmas.append(token.lemma_.lower())
            pos_tags.append((token.text, token.pos_))

        sentences = [sent.text.strip() for sent in doc.sents]
        
        named_entities = [
            NamedEntity(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char
            )
            for ent in doc.ents
        ]

        noun_chunks = [chunk.text for chunk in doc.noun_chunks]

        return ProcessedDocument(
            original_text=text,
            tokens=tokens,
            lemmas=lemmas,
            sentences=sentences,
            named_entities=named_entities,
            noun_chunks=noun_chunks,
            pos_tags=pos_tags
        )
