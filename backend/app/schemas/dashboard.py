from pydantic import BaseModel


class DashboardStats(BaseModel):
    repositories: int
    files_analyzed: int
    reviews: int
    chats: int
