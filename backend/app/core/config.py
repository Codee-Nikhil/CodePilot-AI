"""Central application settings, loaded from environment variables."""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CodePilot AI"
    environment: str = "development"
    database_url: str
    frontend_origin: str = "http://localhost:3000"

    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    encryption_key: str
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/api/github/callback"
    github_oauth_scope: str = "public_repo"

    gemini_api_key: str = ""
    llm_model: str = "gemini-3.5-flash"
    embedding_provider: Literal["local", "gemini"] = "local"
    local_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    gemini_embedding_model: str = "gemini-embedding-001"
    chroma_path: str = "./chroma_data"
    rag_top_k: int = 6


@lru_cache
def get_settings() -> Settings:
    return Settings()
