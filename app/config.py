from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Store API and database settings."""

    app_name: str = "RT Sync API"
    app_env: str = "development"
    api_prefix: str = "/api"
    frontend_origin: str = "http://127.0.0.1:5173"
    database_url: str = ""
    # Opt-in Google login; Vercel Authentication stays enabled until activated.
    rtsync_auth_required: bool = False
    # Two seeded demonstration accounts: PBKDF2(salt:hash) is stored only in
    # Vercel environment variables; plaintext passwords are never committed.
    rtsync_owner_password_hash: str = ""
    rtsync_employee_password_hash: str = ""
    rtsync_session_secret: str = ""
    rtsync_allowed_emails: str = ""
    # Email-based, server-side RBAC; never trust a role sent by the browser.
    rtsync_owner_emails: str = ""
    rtsync_employee_emails: str = ""
    supabase_auth_url: str = "https://zbgomqxlqmcucekjccmt.supabase.co"
    # Server-only publishable API key. Never prefix with VITE_: public REST grants are not hardened.
    supabase_auth_key: str = ""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
