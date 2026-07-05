from pydantic import BaseModel, ConfigDict


class ContactInfo(BaseModel):
    """Extracted contact and social link information."""
    model_config = ConfigDict(frozen=True)

    full_name: str | None
    email: str | None
    phone: str | None
    location: str | None
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None
    leetcode_url: str | None
    hackerrank_url: str | None
    kaggle_url: str | None
