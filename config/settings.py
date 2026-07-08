from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "dev-secret-change-me"
    database_url: str = "sqlite+aiosqlite:///./data/etutor.db"

    stt_provider: str = "local"
    whisper_model: str = "base.en"
    openai_api_key: str = ""

    inference_model: str = "claude-sonnet-5"
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    model_under_8: str = "claude-haiku-4-5-20251001"
    model_8_plus: str = "claude-sonnet-5"

    calibre_web_url: str = "http://localhost:8083"
    calibre_web_admin_user: str = "admin"
    calibre_web_admin_password: str = ""

    class Config:
        env_file = "config/.env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
