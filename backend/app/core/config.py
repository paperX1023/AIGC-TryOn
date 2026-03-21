from pathlib import Path
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

    tryon_api_base_url: str = ""
    tryon_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
