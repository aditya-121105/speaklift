from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ProfileMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    profile_created_at: datetime
    source_filename: str
    is_active: bool
