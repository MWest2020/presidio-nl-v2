import io

import fitz  # PyMuPDF
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def create_test_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_full_document_flow():
    pdf_content = create_test_pdf("My name is John Doe. Contact john@example.com")
    files = {"files": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}

    resp = client.post("/api/v1/documents/upload", files=files)
    assert resp.status_code == 200
    file_id = resp.json()["files"][0]["id"]

    resp = client.get(f"/api/v1/documents/{file_id}/metadata")
    assert resp.status_code == 200

    body = {"pii_entities_to_anonymize": ["PERSON", "EMAIL"]}
    resp = client.post(f"/api/v1/documents/{file_id}/anonymize", json=body)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    resp = client.get(f"/api/v1/documents/{file_id}/download", params={"keep_on_server": True})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
