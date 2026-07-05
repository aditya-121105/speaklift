import threading
import spacy
from typing import Optional


class SpacyResourceManager:
    """
    Thread-safe singleton loader for the spaCy model.
    Loads the model lazily on first request.
    """
    _model: Optional[spacy.Language] = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get_model(cls, model_name: str = "en_core_web_sm") -> spacy.Language:
        """
        Return the shared spaCy model. Loads it if not already loaded.
        """
        if cls._model is None:
            with cls._lock:
                # Double-checked locking
                if cls._model is None:
                    cls._model = spacy.load(model_name)
        return cls._model

    @classmethod
    def is_loaded(cls) -> bool:
        """Check if the model is currently loaded in memory."""
        return cls._model is not None
