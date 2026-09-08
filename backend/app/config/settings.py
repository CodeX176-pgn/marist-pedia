from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Find the root folder of the Marist Pedia project.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Marist Pedia"
    app_version: str = "0.1.0"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Browser security
    cors_origins: str = (
        "http://localhost:5500,"
        "http://127.0.0.1:5500,"
        "http://192.168.18.6:5500"
    )

    allowed_hosts: str = (
        "localhost,"
        "127.0.0.1,"
        "testserver,"
        "192.168.18.6"
    )

    # Upload security
    max_upload_size: int = 10 * 1024 * 1024
    max_filename_length: int = 255

    # Folder where uploaded documents are stored.
    upload_directory: Path = (
        PROJECT_ROOT / "storage" / "uploads"
    )

    # SQLite database file.
    database_file: Path = (
        PROJECT_ROOT / "storage" / "marist_pedia.db"
    )

    # SQLAlchemy connection URL.
    database_url: str = (
        f"sqlite:///{PROJECT_ROOT / 'storage' / 'marist_pedia.db'}"
    )

    # Allowed document types.
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
        """Return configured CORS origins."""
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def allowed_hosts_list(self) -> list[str]:
        """Return configured trusted hosts."""
        return [
            host.strip()
            for host in self.allowed_hosts.split(",")
            if host.strip()
        ]


settings = Settings()
