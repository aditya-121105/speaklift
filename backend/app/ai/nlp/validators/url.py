from urllib.parse import urlparse
from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.validators.base import Validator


class URLValidator(Validator):
    """
    Validates standard URLs (LinkedIn, GitHub, Portfolio, Kaggle, HackerRank, LeetCode, Certifications).
    Clears out URLs that do not match their expected domains or have invalid schemes.
    """

    def _is_valid_url(self, url: str | None, expected_domain: str = "") -> str | None:
        if not url:
            return None
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return None
            if not parsed.netloc or ' ' in parsed.netloc:
                return None
            if expected_domain and expected_domain.lower() not in parsed.netloc.lower():
                return None
            return url
        except Exception:
            return None

    def validate(self, entities: ExtractedEntities) -> ExtractedEntities:
        contact = entities.contact.model_copy(update={
            "linkedin_url": self._is_valid_url(entities.contact.linkedin_url, "linkedin.com"),
            "github_url": self._is_valid_url(entities.contact.github_url, "github.com"),
            "portfolio_url": self._is_valid_url(entities.contact.portfolio_url),
            "leetcode_url": self._is_valid_url(entities.contact.leetcode_url, "leetcode.com"),
            "hackerrank_url": self._is_valid_url(entities.contact.hackerrank_url, "hackerrank.com"),
            "kaggle_url": self._is_valid_url(entities.contact.kaggle_url, "kaggle.com")
        })

        certs = [
            c.model_copy(update={"credential_url": self._is_valid_url(c.credential_url)}) 
            for c in entities.certifications
        ]

        return entities.model_copy(update={
            "contact": contact, 
            "certifications": certs
        })
