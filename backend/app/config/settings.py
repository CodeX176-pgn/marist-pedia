from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Marist Pedia"
    app_version: str = "0.1.0"

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Security / CORS
    cors_origins: str = (
        "http://localhost:5500,"
        "http://127.0.0.1:5500,"
        "http://192.168.18.6:5500"
    )

    # Upload configuration
    max_upload_size: int = 10 * 1024 * 1024

    upload_directory: Path = PROJECT_ROOT / "storage" / "uploads"

    allowed_document_extensions: tuple[str, ...] = (
        ".pdf",
        ".txt",
        ".md",
        ".markdown",
    )

    # Question generation
    question_generator: str = "local"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return configured CORS origins as a clean list."""
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
