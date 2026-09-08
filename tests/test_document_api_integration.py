from io import BytesIO

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_complete_document_processing_flow() -> None:
    """Verify upload, extraction, cleaning, and chunking through the API."""

    upload = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "biology.txt",
                BytesIO(
                    b"Photosynthesis converts light energy into chemical energy."
                ),
                "text/plain",
            )
        },
    )

    assert upload.status_code == 201
    document_id = upload.json()["id"]

    text_response = client.get(
        f"/api/documents/{document_id}/text"
    )
    assert text_response.status_code == 200
    assert "Photosynthesis" in text_response.json()["text"]

    process_response = client.get(
        f"/api/documents/{document_id}/process"
    )
    assert process_response.status_code == 200
    processed = process_response.json()
    assert processed["chunk_count"] >= 1
    assert processed["chunks"][0]["text"]
