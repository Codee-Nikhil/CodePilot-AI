from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    repo_id: int
    paths: list[str] = Field(min_length=1, max_length=15)  # cap: keeps one review affordable and fast


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    path: str
    line: int | None
    severity: str
    category: str
    title: str
    description: str
    suggestion: str | None


class ReviewSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repo_id: int
    paths: list[str]
    status: str
    error: str | None
    summary: str | None
    score: int | None
    created_at: datetime
    completed_at: datetime | None


class ReviewDetail(ReviewSummary):
    findings: list[FindingRead]
