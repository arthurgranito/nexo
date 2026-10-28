from functools import lru_cache
from typing import Literal
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    environment: Literal["development", "staging", "production"] = "development"
    database_url: str = "sqlite:///./nexo.db"
    database_api_url: str = ""
    database_executor_url: str = ""
    redis_url: str = "redis://localhost:6379/0"
    supabase_url: str = ""
    supabase_audience: str = "authenticated"
    dev_auth: bool = False
    dev_token: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]

    @model_validator(mode="after")
    def secure_environment(self):
        if self.dev_auth and (self.environment != "development" or len(self.dev_token) < 24):
            raise ValueError("Dev auth exige development e token com pelo menos 24 caracteres")
        if self.environment != "development" and not self.supabase_url.startswith("https://"):
            raise ValueError("SUPABASE_URL HTTPS é obrigatório fora de development")
        return self

@lru_cache
def settings():
    return Settings()


def api_database_url() -> str:
    cfg = settings()
    return cfg.database_api_url or cfg.database_url


def executor_database_url() -> str:
    cfg = settings()
    return cfg.database_executor_url or cfg.database_url
