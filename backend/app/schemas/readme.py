from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReadmeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    repo_id: int
    content: str
    updated_at: datetime
