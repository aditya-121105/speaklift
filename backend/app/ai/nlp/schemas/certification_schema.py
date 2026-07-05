from pydantic import BaseModel, ConfigDict


class CertificationRecord(BaseModel):
    """A single certification entry."""
    model_config = ConfigDict(frozen=True)

    name: str
    issuer: str | None
    year: int | None
    raw_text: str
    normalized_name: str | None = None
