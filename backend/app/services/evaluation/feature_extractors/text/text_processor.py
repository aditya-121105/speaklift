"""
==============================================================================
Module:
    Text Processor

Sprint:
    Sprint 4 - Evaluation Engine

Purpose:
    Converts raw interview text into a TextDocument using spaCy.

Responsibilities:
    ✔ Normalize text
    ✔ Tokenize
    ✔ Lemmatize
    ✔ Sentence segmentation
    ✔ Named Entity Recognition

Does NOT:
    ✘ Evaluate answers
    ✘ Calculate scores
    ✘ Access database

==============================================================================
Interview Notes

Q. Why isolate spaCy inside TextProcessor?

Answer:

Only one module depends on the NLP library.

Every other module works with SpeakLift's own domain models.

This keeps the project maintainable and allows future NLP
engine replacement with minimal code changes.

==============================================================================
"""

from app.core.nlp import NLPResourceManager
from app.schemas.evaluation.text_document import TextDocument


class TextProcessor:
    """
    Converts raw interview text into a structured TextDocument.
    """

    def process(
        self,
        text: str,
    ) -> TextDocument:
        """
        Process raw interview text.

        Parameters
        ----------
        text:
            Raw interview answer.

        Returns
        -------
        TextDocument
        """

        nlp = NLPResourceManager.get_spacy_model()

        doc = nlp(text)

        # Alphabetic tokens
        tokens = [
            token.text.lower()
            for token in doc
            if token.is_alpha
        ]

        # Lemmas
        lemmas = [
            token.lemma_.lower()
            for token in doc
            if token.is_alpha
        ]

        # Sentences
        sentences = [
            sentence.text.strip()
            for sentence in doc.sents
        ]

        # Named entities
        named_entities = [
            entity.text
            for entity in doc.ents
        ]

        # Stop words
        stop_words = [
            token.text.lower()
            for token in doc
            if token.is_alpha and token.is_stop
        ]

        # Content words
        content_words = [
            token.lemma_.lower()
            for token in doc
            if (
                    token.is_alpha
                    and token.pos_
                    in {
                        "NOUN",
                        "PROPN",
                        "VERB",
                        "ADJ",
                        "ADV",
                    }
            )
        ]

        return TextDocument(
            original_text=text,
            normalized_text=" ".join(
                doc.text.lower().split()
            ),
            tokens=tokens,
            lemmas=lemmas,
            sentences=sentences,
            named_entities=named_entities,
            stop_words=stop_words,
            content_words=content_words,
        )