from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find the root folder of the Marist Pedia project.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "Marist Pedia"
    app_version: str = "0.1.0"

    # Runtime environment controls production-only safety checks.
    environment: str = "development"
    debug: bool = False

    # Server settings.
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Only explicitly listed browser origins may call the API.
    cors_origins: str = (
        "http://localhost:5500,"
        "http://127.0.0.1:5500"
    )

    # Only explicitly listed Host headers are trusted.
    allowed_hosts: str = (
        "localhost,"
        "127.0.0.1,"
        "testserver"
    )

    # Upload security limits.
    max_upload_size: int = 10 * 1024 * 1024
    max_filename_length: int = 255

    # Folder where uploaded documents are stored.
    upload_directory: Path = (
        PROJECT_ROOT / "storage" / "uploads"
    )

    # Default SQLite database location.
    database_file: Path = (
        PROJECT_ROOT / "storage" / "marist_pedia.db"
    )

    # SQLAlchemy database connection URL.
    #
    # DATABASE_URL is kept as an alias because the existing test
    # suite uses it. MARIST_DATABASE_URL is the production-friendly name.
    database_url: str = Field(
        default=f"sqlite:///{PROJECT_ROOT / 'storage' / 'marist_pedia.db'}",
        validation_alias=AliasChoices(
            "DATABASE_URL",
            "MARIST_DATABASE_URL",
        ),
    )

    # Allowed document types.
    allowed_document_extensions: tuple[str, ...] = (
        ".pdf",
        ".txt",
        ".md",
        ".markdown",
    )

    # Teacher/admin API secret.
    # This MUST be replaced before production deployment.
    admin_key: str = "change-this-admin-key"

    # Question generation implementation.
    question_generator: str = "local"

    # FastAPI documentation can be disabled in production.
    docs_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",

        # Environment variables use the MARIST_ prefix.
        env_prefix="MARIST_",

        # Ignore unknown environment variables.
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert the comma-separated CORS setting into a list."""
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def allowed_hosts_list(self) -> list[str]:
        """Convert the comma-separated Host setting into a list."""
        return [
            host.strip()
            for host in self.allowed_hosts.split(",")
            if host.strip()
        ]

    @property
    def is_production(self) -> bool:
        """Return True when the application is running in production."""
        return self.environment.lower() == "production"

    def validate_production(self) -> None:
        """Reject dangerous configuration before production startup."""

        # Development environments do not need these checks.
        if not self.is_production:
            return

        # Never allow the example admin key in production.
        if self.admin_key in {
            "",
            "change-this-admin-key",
        }:
            raise ValueError(
                "MARIST_ADMIN_KEY must be replaced before production startup."
            )

        # Never allow every website to access the production API.
        if "*" in self.cors_origins_list:
            raise ValueError(
                "CORS_ORIGINS must not contain '*' in production."
            )

        # Never trust every Host header in production.
        if "*" in self.allowed_hosts_list:
            raise ValueError(
                "ALLOWED_HOSTS must not contain '*' in production."
            )


# Load the configuration once when the application starts.
settings = Settings()

# Stop immediately if production configuration is unsafe.
settings.validate_production()