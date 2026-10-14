from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Store API and database settings."""

    app_name: str = "RT Sync API"
    app_env: str = "development"
    # Production is a public demo until authenticated business APIs exist.
    # Never expose database records or write operations anonymously.
    public_demo_mode: bool = True
    api_prefix: str = "/api"
    frontend_origin: str = "http://127.0.0.1:5173"
    database_url: str = ""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
