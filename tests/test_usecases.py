import os
import time
from pathlib import Path

import pytest
import requests


def get_base_url() -> str:
    # Prefer explicit env var; default to local dev
    return os.getenv("OPENANONYMISER_BASE_URL", "http://localhost:8080")


def _assert_ok(resp: requests.Response) -> None:
    assert resp.status_code in (200, 201), f"HTTP {resp.status_code}: {resp.text}"


@pytest.mark.integration
def test_health() -> None:
    base = get_base_url()
    resp = requests.get(f"{base}/api/v1/health", timeout=30)
    _assert_ok(resp)
    data = resp.json()
    assert isinstance(data, dict)
    assert data.get("ping") == "pong"


@pytest.mark.integration
def test_analyze_text_spacy() -> None:
    base = get_base_url()
    payload = {
        "text": "Jan Jansen woont op Kerkstraat 10, 1234 AB Amsterdam. IBAN: NL91ABNA0417164300.",
        "language": "nl",
        "entities": ["PERSON", "IBAN", "ADDRESS"],
        "nlp_engine": "spacy",
    }
    resp = requests.post(f"{base}/api/v1/analyze", json=payload, timeout=60)
    _assert_ok(resp)
    data = resp.json()
    assert "pii_entities" in data
    # Expect at least one entity recognized
    assert isinstance(data["pii_entities"], list)
    assert len(data["pii_entities"]) >= 1


@pytest.mark.integration
def test_anonymize_text() -> None:
    base = get_base_url()
    payload = {
        "text": "Mail Jan op jan.jansen@example.com of bel 0612345678.",
        "language": "nl",
        "anonymization_strategy": "replace",
    }
    resp = requests.post(f"{base}/api/v1/anonymize", json=payload, timeout=60)
    _assert_ok(resp)
    data = resp.json()
    assert "original_text" in data and "anonymized_text" in data
    assert data["original_text"] != data["anonymized_text"]
    assert isinstance(data.get("entities_found", []), list)


@pytest.mark.integration
def test_document_flow_upload_anonymize_download(tmp_path: Path) -> None:
    base = get_base_url()

    # Use bundled test.pdf if present, else skip
    repo_pdf = Path("test.pdf")
    if not repo_pdf.exists():
        pytest.skip("test.pdf not found in repo root")

    # 1) Upload
    with repo_pdf.open("rb") as fh:
        files = {"files": ("test.pdf", fh, "application/pdf")}
        resp = requests.post(
            f"{base}/api/v1/documents/upload", files=files, timeout=120
        )
    _assert_ok(resp)
    up = resp.json()
    assert "files" in up and isinstance(up["files"], list) and len(up["files"]) >= 1
    file_id = up["files"][0]["id"]
    assert file_id

    # 2) Anonymize
    anon_payload = {
        "pii_entities_to_anonymize": [
            "PERSON",
            "EMAIL",
            "PHONE_NUMBER",
            "IBAN",
            "ADDRESS",
        ]
    }
    resp = requests.post(
        f"{base}/api/v1/documents/{file_id}/anonymize", json=anon_payload, timeout=180
    )
    _assert_ok(resp)
    anon = resp.json()
    assert anon.get("status") in {"ok", "success", "completed"}

    # Optional delay if processing is async in some environments
    time.sleep(1)

    # 3) Download
    out_pdf = tmp_path / "output.pdf"
    resp = requests.get(f"{base}/api/v1/documents/{file_id}/download", timeout=120)
    _assert_ok(resp)
    # Some deployments may return FileResponse (binary) or a JSON envelope (rare).
    # Prefer binary write if possible.
    try:
        content = resp.content
        assert content and len(content) > 0
        out_pdf.write_bytes(content)
        assert out_pdf.exists() and out_pdf.stat().st_size > 0
    except Exception as exc:
        raise AssertionError(f"Failed to store downloaded file: {exc}")
