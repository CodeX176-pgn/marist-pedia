def test_production_rejects_default_admin_key() -> None:
    """Production must never use the example admin secret."""

    from app.config.settings import Settings

    settings = Settings(
        environment="production",
        admin_key="change-this-admin-key",
    )

    try:
        settings.validate_production()
    except ValueError as exc:
        assert "MARIST_ADMIN_KEY" in str(exc)
    else:
        raise AssertionError(
            "Production accepted the default admin key"
        )


def test_production_accepts_explicit_safe_configuration() -> None:
    """A properly configured production environment should start."""

    from app.config.settings import Settings

    settings = Settings(
        environment="production",
        admin_key="a-long-production-secret-value",
        cors_origins="https://maristpedia.example.com",
        allowed_hosts="maristpedia.example.com",
    )

    settings.validate_production()


def test_readiness_endpoint_reports_database_health() -> None:
    """The readiness endpoint should verify database access."""

    from app.main import app
    from fastapi.testclient import TestClient

    response = TestClient(app).get("/health/ready")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready",
        "service": "Marist Pedia",
        "database": "ok",
    }