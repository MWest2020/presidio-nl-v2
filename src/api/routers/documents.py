import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi import File as FastAPIFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.api.config import settings
from src.api.crud import anonymization_event, document, tag
from src.api.database import AnonymizationEvent, Document, Tag, get_db
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
    db: Session = Depends(get_db),
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

        # Create document in database
        db_document = Document(
            id=file_id,
            filename=file.filename or f"{file_id}.pdf",
            content_type=file.content_type or "application/pdf",
            uploaded_at=datetime.now(),
            source_path=str(source_path),
            anonymized_path=None,
        )

        # Add tags
        db_tags = []
        for tag_name in tags or []:
            tag = Tag(id=uuid.uuid4().hex, name=tag_name, document_id=file_id)
            db_tags.append(tag)
            db_document.tags.append(tag)

        # Store entities in memory attribute (not persisted to DB)
        db_document._entities = entities

        # Add to DB
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        # Convert to DTO for API response
        stored_tags = [DocumentTagDto(id=tag.id, name=tag.name) for tag in db_tags]
        doc_meta = DocumentDto(
            id=file_id,
            filename=db_document.filename,
            content_type=db_document.content_type,
            uploaded_at=db_document.uploaded_at,
            tags=stored_tags,
            pii_entities=unique,
        )

        docs.append(doc_meta)

    return AddDocumentResponseSuccess(files=docs)


@documents_router.get("/{file_id}/metadata", response_model=DocumentDto)
async def get_document_metadata(
    file_id: str, db: Session = Depends(get_db)
) -> DocumentDto:
    """Get metadata for a specific document. Same response as upload."""
    doc = document.get_by_id(db, file_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Convert DB model to DTO
    tags = [DocumentTagDto(id=tag.id, name=tag.name) for tag in doc.tags]

    # Create DTO with only unique entities
    unique_entities = []
    if hasattr(doc, "_entities") and doc._entities:
        seen = set()
        for ent in doc._entities:
            key = (ent["entity_type"], ent["text"])
            if key not in seen:
                unique_entities.append(
                    {"entity_type": ent["entity_type"], "text": ent["text"]}
                )
                seen.add(key)

    return DocumentDto(
        id=doc.id,
        filename=doc.filename,
        content_type=doc.content_type,
        uploaded_at=doc.uploaded_at,
        tags=tags,
        pii_entities=unique_entities,
    )


@documents_router.post("/{file_id}/anonymize")
async def anonymize_document(
    file_id: str,
    request_body: DocumentAnonymizationRequest,
    db: Session = Depends(get_db),
) -> DocumentAnonymizationResponse:
    """Anonymize a specific document."""
    doc = document.get_by_id(db, file_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    source_path = doc.source_path
    analyzer = ModularTextAnalyzer()

    # Get entities from the document or extract them
    entities = getattr(doc, "_entities", None)
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
        doc._entities = entities

    selected = []
    for e in entities:
        if e["entity_type"] in request_body.pii_entities_to_anonymize:
            e_copy = e.copy()
            for field in ("start", "end", "score"):
                if field in e_copy:
                    e_copy[field] = str(e_copy[field])
            selected.append(e_copy)

    mapping = {e["text"]: e["entity_type"].lower() for e in selected}

    anonym_dir = Path("temp/anonymized")
    anonym_dir.mkdir(parents=True, exist_ok=True)
    out_path = anonym_dir / f"{file_id}.pdf"

    start = time.perf_counter()
    try:
        key = settings.CRYPTO_KEY.decode()
        pdf_xmp.anonymize_pdf(source_path, str(out_path), mapping, key)
        status_text = "success"
    except Exception as exc:  # pragma: no cover - depends on external libs
        status_text = f"failed: {exc}"
    end = time.perf_counter()

    # Update document in database
    doc.anonymized_path = str(out_path)

    # Create anonymization event
    event = AnonymizationEvent(
        document_id=file_id,
        anonymized_at=datetime.now(),
        time_taken=int(end - start),
        status=status_text,
    )
    event._pii_entities = selected

    # Save to database
    db.add(event)
    db.commit()
    db.refresh(doc)

    return DocumentAnonymizationResponse(
        id=file_id,
        filename=doc.filename,
        anonymized_at=event.anonymized_at,
        time_taken=event.time_taken,
        status=event.status,
        pii_entities=selected,
    )


@documents_router.get("/{file_id}/download")
async def download_document(
    file_id: str, keep_on_server: bool = False, db: Session = Depends(get_db)
) -> FileResponse:
    """Download a specific document.

    Now we can use FastAPI's FileResponse to serve the file directly from disk;
    however in the future, we may use StreamingResponse to stream large files (from memory or disk) to the client.
    """
    doc = db.query(Document).filter(Document.id == file_id).first()
    if not doc or not doc.anonymized_path:
        raise HTTPException(status_code=404, detail="Document not anonymized")

    path = Path(doc.anonymized_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    background = BackgroundTasks()
    if not keep_on_server:
        background.add_task(path.unlink)

    return FileResponse(path=str(path), filename=path.name, background=background)
