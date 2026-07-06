import json
import threading
from pathlib import Path
from typing import Optional


class TaxonomyResourceManager:
    """
    Thread-safe singleton loader for taxonomy and synonym resources.
    Loads the resources lazily on first request.
    """
    _taxonomy: Optional[dict[str, tuple[str, str]]] = None
    _synonyms: Optional[dict[str, str]] = None
    _technology_categories = {
        "databases", "cloud", "devops", "tools", "operating_systems"
    }
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def load_if_needed(cls, taxonomy_dir: Path | None = None) -> None:
        if cls._taxonomy is None or cls._synonyms is None:
            with cls._lock:
                if cls._taxonomy is None or cls._synonyms is None:
                    if taxonomy_dir is None:
                        taxonomy_dir = Path(__file__).parent / "taxonomy"
                    
                    taxonomy = {}
                    for path in taxonomy_dir.glob("*.json"):
                        if path.name == "synonyms.json":
                            continue
                        category = path.stem
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                skills_list = json.load(f)
                                for skill in skills_list:
                                    taxonomy[skill.lower()] = (skill, category)
                        except Exception:
                            pass
                    
                    synonyms = {}
                    synonyms_path = taxonomy_dir / "synonyms.json"
                    if synonyms_path.exists():
                        try:
                            with open(synonyms_path, "r", encoding="utf-8") as f:
                                synonyms = json.load(f)
                        except Exception:
                            pass
                    
                    cls._taxonomy = taxonomy
                    cls._synonyms = synonyms

    @classmethod
    def get_taxonomy(cls, taxonomy_dir: Path | None = None) -> dict[str, tuple[str, str]]:
        """Return the lowercase_name -> (normalized_name, category) map."""
        cls.load_if_needed(taxonomy_dir)
        return cls._taxonomy  # type: ignore

    @classmethod
    def get_synonyms(cls, taxonomy_dir: Path | None = None) -> dict[str, str]:
        """Return the pattern_str -> normalized_name map."""
        cls.load_if_needed(taxonomy_dir)
        return cls._synonyms  # type: ignore

    @classmethod
    def get_technology_categories(cls) -> set[str]:
        """Return the set of categories considered as technologies."""
        return cls._technology_categories
