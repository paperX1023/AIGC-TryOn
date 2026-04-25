from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "AIGC Try-On Backend"
    app_version: str = "0.1.0"

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    openai_vision_model: str = ""

    pose_model_path: str = str(BASE_DIR / "models" / "pose_landmarker_lite.task")
    upload_dir: str = str(BASE_DIR / "uploads")

    database_url: str = ""
    database_auto_create_tables: bool = True
    db_host: str = ""
    db_port: int = 3306
    db_user: str = ""
    db_password: str = ""
    db_name: str = "aigc_tryon"

    auth_secret_key: str = "aigc-tryon-dev-secret"
    auth_token_expire_minutes: int = 60 * 24 * 7

    tryon_api_base_url: str = ""
    tryon_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8"
    )

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        if not self.db_host or not self.db_user:
            return ""

        username = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        database = quote_plus(self.db_name or "aigc_tryon")
        return (
            f"mysql+pymysql://{username}:{password}"
            f"@{self.db_host}:{self.db_port}/{database}?charset=utf8mb4"
        )


settings = Settings()
