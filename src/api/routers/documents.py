import os
from typing import Optional

from fastapi import APIRouter, Response, UploadFile, status
from fastapi import File as FastAPIFile

from src.api.config import settings
from src.api.dtos import (
    AddDocumentResponse,
    AddDocumentResponseInvalid,
    AddDocumentResponseSuccess,
    DocumentDto,
    DocumentTagDto,
)

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

    # TODO: read file here
    content = await file.read()
    await file.close()

    # TODO: analyze file content for PII entities

    # TODO: format tags

    # TODO: format response

    f = file

    return AddDocumentResponseSuccess(
        files=[
            DocumentDto(
                id=f.id,
                filename=f.filename,
                blob_name=f.blob_name,
                created_at=f.created_at,
                tags=[DocumentTagDto(id=tag.id, name=tag.name) for tag in f.tags],
                pii_entities=f.pii_entities,
            )
        ]
    )


@documents_router.get("/{file_id}/metadata", response_model=DocumentDto)
async def get_document_metadata(file_id: str) -> DocumentDto:
    """Get metadata for a specific document. Same response as upload."""
    # TODO: implement
    return DocumentDto()
