from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """รวมค่าตั้งค่าของ API และ frontend ที่อนุญาตให้เรียกใช้งาน"""

    app_name: str = "RT Sync API"
    app_env: str = "development"
    api_prefix: str = "/api"
    frontend_origin: str = "http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
