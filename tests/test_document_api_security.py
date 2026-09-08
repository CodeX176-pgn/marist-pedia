from io import BytesIO

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_upload_rejects_unsupported_file_type() -> None:
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "program.exe",
                BytesIO(b"not an executable upload"),
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_rejects_fake_pdf() -> None:
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "lesson.pdf",
                BytesIO(b"This is not a PDF"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert "valid PDF" in response.json()["detail"]


def test_upload_accepts_valid_text_document() -> None:
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "lesson.txt",
                BytesIO(
                    b"Photosynthesis converts light energy "
                    b"into chemical energy."
                ),
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["extension"] == ".txt"
    assert data["size"] > 0
    assert data["original_filename"] == "lesson.txt"
