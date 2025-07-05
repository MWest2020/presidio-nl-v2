import hashlib
import logging
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import pymupdf
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
from src.api.crud import (
    create_anonymization_event,
    create_document,
    create_tag,
    get_document,
    update_document_anonymized_path,
)
from src.api.dependencies import get_db
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

logger = logging.getLogger(__name__)
documents_router = APIRouter(prefix="/documents", tags=["documents"])

analyzer = ModularTextAnalyzer()


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
    # username: str = Depends(get_user),
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

        text = pdf_xmp.extract_text_from_pdf(source_path)

        entities, unique = await pdf_xmp.extract_unique_entities(
            text=text, analyzer=analyzer
        )

        # Create document in database
        db_document = create_document(
            db,
            id=file_id,
            filename=file.filename or f"{file_id}.pdf",
            content_type=file.content_type or "application/pdf",
            source_path=str(source_path),
            anonymized_path=None,
        )

        db_tags = []
        for tag_name in tags or []:
            tag_id = uuid.uuid4().hex
            tag = create_tag(db, tag_id, tag_name, file_id)
            db_tags.append(tag)

        db_document._entities = entities

        stored_tags = [
            DocumentTagDto(id=str(tag.id), name=str(tag.name)) for tag in db_tags
        ]
        doc_meta = DocumentDto(
            id=file_id,
            filename=str(db_document.filename),
            content_type=str(db_document.content_type),
            uploaded_at=datetime.now(),  # Use current time for response
            tags=stored_tags,
            pii_entities=unique,
        )

        docs.append(doc_meta)

    return AddDocumentResponseSuccess(files=docs)


@documents_router.post("/deanonymize")
async def deanonymize_document(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    # username: str = Depends(get_user),
) -> FileResponse:
    """The endpoint where the user can submit a document to deanonymize.

    The document contains metadata that was previously anonymized.
    The endpoint returns the original document with metadata restored.
    """
    if file.filename is None or (
        os.path.splitext(file.filename)[1][1:]
        not in settings.SUPPORTED_UPLOAD_EXTENSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Only files with the following extensions are supported: {', '.join(settings.SUPPORTED_UPLOAD_EXTENSIONS)}",
        )

    content = await file.read()
    await file.close()

    # Create temp file for the uploaded anonymized document
    temp_dir = Path("temp/deanonymize")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique ID for this deanonymization process
    process_id = uuid.uuid4().hex
    anon_path = temp_dir / f"{process_id}_anonymized.pdf"
    deanon_path = temp_dir / f"{process_id}_deanonymized.pdf"

    # Save the uploaded file
    with open(anon_path, "wb") as f:
        f.write(content)

    # Extract annotations from the anonymized PDF
    try:
        start = time.perf_counter()
        # Get the key for decryption
        key = settings.CRYPTO_KEY.decode()
        hashed_key = hashlib.sha256(key.encode()).digest()

        # Extract the annotations with encrypted entities
        annotations = pdf_xmp.extract_annotations(
            str(anon_path), decryption_key=hashed_key
        )

        if not annotations:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No anonymization metadata found in the document",
            )

        # Open the PDF document for editing
        doc = pymupdf.open(str(anon_path))

        # Process each annotation to restore original text
        for ann in annotations:
            if "entity" in ann and "Page" in ann and "Rect" in ann:
                page_num = int(ann["Page"]) - 1  # Pages are 0-indexed in PyMuPDF
                if 0 <= page_num < len(doc):
                    page = doc[page_num]

                    # Parse the rectangle coordinates
                    rect_str = ann["Rect"]
                    coords = [float(c) for c in rect_str.split(",")]
                    if len(coords) == 4:
                        rect = pymupdf.Rect(*coords)

                        # Remove any existing text in the redacted area
                        page.add_redact_annot(rect, fill=(1, 1, 1))
                        page.apply_redactions()

                        # Insert the original entity text
                        original_text = ann["entity"]
                        page.insert_textbox(
                            rect, original_text, fontsize=12, color=(0, 0, 0)
                        )

        # Save the deanonymized document
        doc.save(str(deanon_path), incremental=False)
        doc.close()

        end = time.perf_counter()
        logger.info(f"Deanonymization completed in {end - start:.2f} seconds")

        # Return the deanonymized file
        background = BackgroundTasks()
        if not settings.KEEP_TEMP_FILES:
            background.add_task(lambda: anon_path.unlink(missing_ok=True))
            background.add_task(lambda: deanon_path.unlink(missing_ok=True))

        return FileResponse(
            path=str(deanon_path),
            filename=f"deanonymized_{file.filename}"
            if file.filename
            else "deanonymized.pdf",
            media_type="application/pdf",
            background=background,
        )
    except HTTPException as http_exc:
        # Clean up temporary files in case of HTTP error
        if anon_path.exists():
            anon_path.unlink()
        if deanon_path.exists():
            deanon_path.unlink()

        logger.error(
            f"HTTP error during deanonymization: {http_exc.detail}", exc_info=True
        )
        raise http_exc

    except Exception as e:
        # Clean up temporary files in case of error
        if anon_path.exists():
            anon_path.unlink()
        if deanon_path.exists():
            deanon_path.unlink()

        logger.error(f"Error during deanonymization: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deanonymize document: {str(e)}",
        )


@documents_router.get("/{file_id}/metadata", response_model=DocumentDto)
async def get_document_metadata(
    file_id: str,
    get_pii_entities: bool = False,
    db: Session = Depends(get_db),
    # username: str = Depends(get_user),
) -> DocumentDto:
    """Get metadata for a specific document. Same response as upload."""
    doc = get_document(db, file_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    tags = [DocumentTagDto(id=str(tag.id), name=str(tag.name)) for tag in doc.tags]

    if get_pii_entities:
        text = pdf_xmp.extract_text_from_pdf(Path(doc.source_path))
        _, unique_entities = await pdf_xmp.extract_unique_entities(
            text=text, analyzer=analyzer
        )
    else:
        unique_entities = []

    return DocumentDto(
        id=str(doc.id),
        filename=str(doc.filename),
        content_type=str(doc.content_type),
        uploaded_at=datetime.now(),  # Use current time as fallback
        tags=tags,
        pii_entities=unique_entities,
    )


@documents_router.post("/{file_id}/anonymize")
async def anonymize_document(
    file_id: str,
    request_body: DocumentAnonymizationRequest,
    db: Session = Depends(get_db),
    # username: str = Depends(get_user),
) -> DocumentAnonymizationResponse:
    """Anonymize a specific document."""
    doc = get_document(db, file_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    source_path = doc.source_path
    analyzer = ModularTextAnalyzer()

    entities = getattr(doc, "_entities", None)
    if not entities:
        text = ""
        try:
            import pymupdf

            pdf_doc = pymupdf.open(source_path)
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
        logger.info(
            f"Starting anonymization for document {file_id} with {len(mapping)} entities"
        )

        # Verify the source path exists
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file {source_path} not found")

        # Ensure the output directory exists
        anonym_dir.mkdir(parents=True, exist_ok=True)

        # Run the anonymization process
        occurrences = pdf_xmp.anonymize_pdf(
            str(source_path), str(out_path), mapping, key
        )

        # Check if the output file was created successfully
        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            raise ValueError("Anonymization failed to produce valid output file")

        # Verify the number of occurrences matches expected
        if len(occurrences) != len(mapping):
            logger.warning(
                f"Only {len(occurrences)} out of {len(mapping)} entities were processed"
            )

        status_text = f"success ({len(occurrences)} entities processed)"
    except FileNotFoundError as exc:
        logger.error(f"File not found error: {exc}", exc_info=True)
        status_text = f"failed: {exc}"
    except ValueError as exc:
        logger.error(f"Value error during anonymization: {exc}", exc_info=True)
        status_text = f"failed: {exc}"
    except Exception as exc:  # pragma: no cover - depends on external libs
        logger.error(f"Unexpected error during anonymization: {exc}", exc_info=True)
        status_text = f"failed: {exc}"
    end = time.perf_counter()

    # Check if anonymization was successful before updating the database
    if status_text.startswith("failed"):
        # Remove the output file if it exists but anonymization failed
        if os.path.exists(out_path):
            os.unlink(out_path)

        # Create anonymization event to record the failure
        event = create_anonymization_event(
            db,
            document_id=file_id,
            time_taken=int(end - start),
            status=status_text,
        )
        event._pii_entities = selected

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document anonymization failed: {status_text}",
        )

    # Update document in database with the new anonymized path
    updated_doc = update_document_anonymized_path(db, file_id, str(out_path))

    # Create anonymization event to record the success
    event = create_anonymization_event(
        db,
        document_id=file_id,
        time_taken=int(end - start),
        status=status_text,
    )
    event._pii_entities = selected

    return DocumentAnonymizationResponse(
        id=file_id,
        filename=str(updated_doc.filename) if updated_doc else "",
        anonymized_at=datetime.now(),  # Use current time for response
        time_taken=int(end - start),
        status=status_text,
        pii_entities=selected,
    )


@documents_router.get("/{file_id}/download")
async def download_document(
    file_id: str,
    keep_on_server: bool = False,
    db: Session = Depends(get_db),
    # username: str = Depends(get_user),
) -> FileResponse:
    """Download a specific document.

    Now we can use FastAPI's FileResponse to serve the file directly from disk;
    however in the future, we may use StreamingResponse to stream large files (from memory or disk) to the client.
    """
    doc = get_document(db, file_id)
    if not doc or not doc.anonymized_path:
        raise HTTPException(status_code=404, detail="Document not anonymized")

    path = Path(str(doc.anonymized_path))
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    background = BackgroundTasks()
    if not keep_on_server:
        background.add_task(path.unlink)
        source_path = Path(str(doc.source_path))
        background.add_task(source_path.unlink)

    return FileResponse(path=str(path), filename=path.name, background=background)
