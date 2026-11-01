from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CODEPILOT_", env_file=".env", extra="ignore")
    api_base: str = "https://your-provider.example/v1"
    api_key: str = ""
    model: str = ""
    model_timeout: float = Field(default=60, ge=1, le=300)
    database: str = "artifacts/codepilot.sqlite3"
    sandbox_image: str = "course-codepilot-sandbox:0.1"
    execution_timeout: float = Field(default=15, ge=1, le=120)
    backend_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
