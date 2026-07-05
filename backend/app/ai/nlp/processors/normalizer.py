import json
from pathlib import Path
import re
from app.ai.nlp.schemas.processed_document import ProcessedDocument


class Normalizer:
    """
    Resolves synonyms and canonicalizes formats 
    from the processed document to produce a normalized text string.
    """

    def __init__(self, synonyms_path: Path | None = None) -> None:
        if synonyms_path is None:
            # Default to the taxonomy directory in the package
            current_dir = Path(__file__).parent
            synonyms_path = current_dir.parent / "resources" / "taxonomy" / "synonyms.json"

        with open(synonyms_path, "r", encoding="utf-8") as f:
            self._synonyms = json.load(f)

    def normalize(self, processed: ProcessedDocument) -> str:
        """
        Normalize the original text using the extracted features and synonym maps.
        """
        text = processed.original_text

        for pattern, replacement in self._synonyms.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

