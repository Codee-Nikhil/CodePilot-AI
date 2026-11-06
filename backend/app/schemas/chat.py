from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class ChatRequest(BaseModel):
    repo_id: int
    chat_id: int | None = None
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class SourceRef(BaseModel):
    path: str
    start_line: int
    end_line: int


class ChatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repo_id: int
    title: str
    created_at: datetime


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    sources: list[SourceRef] | None
    created_at: datetime


class ChatDetail(ChatRead):
    messages: list[MessageRead]
