"""ไฟล์ตั้งค่าหลักของ backend และค่าการเชื่อมต่อบริการต่าง ๆ"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """รวมค่าตั้งค่าของ API, frontend และฐานข้อมูล"""

    app_name: str = "RT Sync API"
    app_env: str = "development"
    api_prefix: str = "/api"
    frontend_origin: str = "http://127.0.0.1:5173"
    database_url: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
