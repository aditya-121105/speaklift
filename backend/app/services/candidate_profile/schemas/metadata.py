from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProfileMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    pipeline_version: str
    profile_version: str
    generated_timestamp: datetime
    average_confidence: float
    processing_duration_ms: int
