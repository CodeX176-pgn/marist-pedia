from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Marist Pedia"
    app_version: str = "0.1.0"

    max_upload_size: int = 10 * 1024 * 1024

    upload_directory: Path = PROJECT_ROOT / "storage" / "uploads"

    allowed_document_extensions: tuple[str, ...] = (
        ".pdf",
        ".txt",
        ".md",
        ".markdown",
    )

    question_generator: str = "local"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
