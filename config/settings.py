from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache

_INSECURE_DEFAULTS = {"dev-secret-change-me", "change-me"}


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "dev-secret-change-me"
    parent_password: str = "change-me-in-env"

    @field_validator("secret_key")
    @classmethod
    def _secret_key_must_be_set(cls, v: str) -> str:
        if v in _INSECURE_DEFAULTS:
            import warnings
            warnings.warn(
                "SECRET_KEY is using the insecure default. Set SECRET_KEY in config/.env before deploying.",
                stacklevel=2,
            )
        return v
    database_url: str = "sqlite+aiosqlite:///./data/etutor.db"

    stt_provider: str = "local"
    whisper_model: str = "base.en"
    openai_api_key: str = ""

    inference_model: str = "claude-sonnet-5"
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    model_under_8: str = "claude-haiku-4-5-20251001"
    model_8_plus: str = "claude-sonnet-5"

    calibre_web_url: str = "http://192.168.0.25:8083"
    calibre_web_admin_user: str = "admin"
    calibre_web_admin_password: str = ""

    class Config:
        env_file = "config/.env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
