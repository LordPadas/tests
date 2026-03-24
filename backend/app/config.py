from __future__ import annotations

from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql://postgres:postgres@db:5432/app"
    OLLAMA_HOST: str = "http://ollama:11434"
    ROCKETCHAT_URL: str = "http://rocketchat:3000"
    DEBUG: bool = False
    SECRET_KEY: str = "change_me_in_prod"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
