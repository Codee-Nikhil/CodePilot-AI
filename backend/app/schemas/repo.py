from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepoImport(BaseModel):
    full_name: str = Field(pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", max_length=200)


class RepoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    github_id: int
    full_name: str
    name: str
    description: str | None
    language: str | None
    default_branch: str
    html_url: str
    is_private: bool
    stars: int
    last_synced_at: datetime | None
    created_at: datetime
    index_status: str
    index_error: str | None
    indexed_at: datetime | None


class RemoteRepo(BaseModel):
    github_id: int
    full_name: str
    description: str | None
    language: str | None
    is_private: bool
    stars: int
    updated_at: str | None
    imported: bool


class SyncResult(BaseModel):
    added: int
    updated: int
    removed: int


class FileNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    path: str
    size: int
    language: str | None


class FileContent(FileNode):
    content: str
