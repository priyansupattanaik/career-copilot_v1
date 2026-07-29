from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="backend/.env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Career Copilot API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    frontend_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_secret_key: str = ""
    supabase_service_role_key: str = ""
    document_max_bytes: int = 10 * 1024 * 1024
    avatar_max_bytes: int = 5 * 1024 * 1024
    interview_media_max_bytes: int = 250 * 1024 * 1024
    document_bucket: str = "candidate-documents"
    avatar_bucket: str = "candidate-avatars"
    interview_bucket: str = "interview-media"

    @field_validator("frontend_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_publishable_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
