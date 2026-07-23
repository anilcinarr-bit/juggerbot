from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Telegram
    tg_api_id: int
    tg_api_hash: str
    tg_session_name: str = "userbot_session"
    tg_admin_user_id: int | None = None

    @field_validator("tg_admin_user_id", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        return None if v == "" else v

    # DB
    database_url: str = "sqlite+aiosqlite:///./junction.db"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:latest"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Application settings
    app_name: str = "Project Atlas"
    version: str = "0.1.0"
    log_level: str = "INFO"


settings = Settings()