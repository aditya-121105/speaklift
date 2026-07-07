from pydantic import BaseModel, ConfigDict
from enum import Enum

class RemoteType(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ON_SITE = "ON_SITE"
    UNKNOWN = "UNKNOWN"

class JobIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)
    job_title: str | None
    raw_title: str | None
    location: str | None
    remote_type: RemoteType | None
