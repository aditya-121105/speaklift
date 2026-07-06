from pydantic import BaseModel, ConfigDict


class ContactInformation(BaseModel):
    model_config = ConfigDict(frozen=True)
    email: str | None = None
    phone: str | None = None
    location: str | None = None


class SocialProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    kaggle: str | None = None
    leetcode: str | None = None
    hackerrank: str | None = None


class IdentityProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    full_name: str | None = None
    contact: ContactInformation
    social: SocialProfile
