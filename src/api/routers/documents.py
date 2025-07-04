import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi import File as FastAPIFile
from fastapi.responses import FileResponse

from src.api.config import settings
from src.api.dtos import (
    AddDocumentResponse,
    AddDocumentResponseInvalid,
    AddDocumentResponseSuccess,
    DocumentAnonymizationRequest,
    DocumentAnonymizationResponse,
    DocumentDto,
    DocumentTagDto,
)
from src.api.services.text_analyzer import ModularTextAnalyzer
from src.api.utils import pdf_xmp

_DOCUMENT_STORE: dict[str, dict] = {}

documents_router = APIRouter(prefix="/documents", tags=["documents"])


@documents_router.post(
    "/upload",
    responses={
        status.HTTP_200_OK: {
            "model": AddDocumentResponseSuccess,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": AddDocumentResponseInvalid,
        },
    },
)
async def upload_document(
    response: Response,
    files: list[UploadFile] = FastAPIFile(...),
    tags: Optional[list[str]] = None,
) -> AddDocumentResponse:
    if any(
        f
        for f in files
        if f.filename is None
        or os.path.splitext(f.filename)[1][1:]
        not in settings.SUPPORTED_UPLOAD_EXTENSIONS
    ):
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        return AddDocumentResponseInvalid(
            message=f"Only files with the following extensions are supported: {', '.join(settings.SUPPORTED_UPLOAD_EXTENSIONS)}"
        )

    analyzer = ModularTextAnalyzer()
    docs: list[DocumentDto] = []

    for file in files:
        content = await file.read()
        await file.close()

        file_id = uuid.uuid4().hex
        source_dir = Path("temp/source")
        source_dir.mkdir(parents=True, exist_ok=True)
        source_path = source_dir / f"{file_id}.pdf"
        with open(source_path, "wb") as f:
            f.write(content)

        text = ""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(str(source_path))
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
        except Exception:
            text = ""

        entities = analyzer.analyze_text(text) if text else []
        unique: list[dict[str, str]] = []
        seen = set()
        for ent in entities:
            key = (ent["entity_type"], ent["text"])
            if key not in seen:
                unique.append({"entity_type": ent["entity_type"], "text": ent["text"]})
                seen.add(key)

        stored_tags = [DocumentTagDto(id=uuid.uuid4().hex, name=t) for t in tags or []]

        doc_meta = DocumentDto(
            id=file_id,
            filename=file.filename or f"{file_id}.pdf",
            content_type=file.content_type or "application/pdf",
            uploaded_at=datetime.utcnow(),
            tags=stored_tags,
            pii_entities=unique,
        )

        _DOCUMENT_STORE[file_id] = {
            "meta": doc_meta,
            "source_path": str(source_path),
            "anonymized_path": None,
            "entities": entities,
        }

        docs.append(doc_meta)

    return AddDocumentResponseSuccess(files=docs)


@documents_router.get("/{file_id}/metadata", response_model=DocumentDto)
async def get_document_metadata(file_id: str) -> DocumentDto:
    """Get metadata for a specific document. Same response as upload."""
    doc = _DOCUMENT_STORE.get(file_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc["meta"]


@documents_router.post("/{file_id}/anonymize")
async def anonymize_document(
    file_id: str, request_body: DocumentAnonymizationRequest
) -> DocumentAnonymizationResponse:
    """Anonymize a specific document."""
    doc = _DOCUMENT_STORE.get(file_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    source_path = doc["source_path"]
    analyzer = ModularTextAnalyzer()

    entities = doc.get("entities")
    if not entities:
        text = ""
        try:
            import fitz

            pdf_doc = fitz.open(source_path)
            text = "\n".join(p.get_text() for p in pdf_doc)
            pdf_doc.close()
        except Exception:
            text = ""
        entities = analyzer.analyze_text(text) if text else []
        doc["entities"] = entities

    selected = [
        e for e in entities if e["entity_type"] in request_body.pii_entities_to_anonymize
    ]
    mapping = {e["text"]: e["entity_type"].lower() for e in selected}

    anonym_dir = Path("temp/anonymized")
    anonym_dir.mkdir(parents=True, exist_ok=True)
    out_path = anonym_dir / f"{file_id}.pdf"

    start = time.perf_counter()
    try:
        key = (settings.CRYPTO_KEY or b"secret").decode()
        pdf_xmp.anonymize_pdf(source_path, str(out_path), mapping, key)
        status_text = "success"
    except Exception as exc:  # pragma: no cover - depends on external libs
        status_text = f"failed: {exc}"
    end = time.perf_counter()

    doc["anonymized_path"] = str(out_path)

    return DocumentAnonymizationResponse(
        id=file_id,
        filename=doc["meta"].filename,
        anonymized_at=datetime.utcnow(),
        time_taken=int(end - start),
        status=status_text,
        pii_entities=selected,
    )


@documents_router.get("/{file_id}/download")
async def download_document(
    file_id: str, keep_on_server: bool = False
) -> FileResponse:
    """Download a specific document.

    Now we can use FastAPI's FileResponse to serve the file directly from disk;
    however in the future, we may use StreamingResponse to stream large files (from memory or disk) to the client.
    """
    doc = _DOCUMENT_STORE.get(file_id)
    if not doc or not doc.get("anonymized_path"):
        raise HTTPException(status_code=404, detail="Document not anonymized")

    path = Path(doc["anonymized_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    background = BackgroundTasks()
    if not keep_on_server:
        background.add_task(path.unlink)

    return FileResponse(path=str(path), filename=path.name, background=background)
