import os
from typing import Optional

from fastapi import APIRouter, Response, UploadFile, status
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

documents_router = APIRouter(prefix="/documents", tags=["documents"])


# @documents_router.post(
#     "/upload",
#     responses={
#         status.HTTP_200_OK: {
#             "model": AddDocumentResponseSuccess,
#         },
#         status.HTTP_422_UNPROCESSABLE_ENTITY: {
#             "model": AddDocumentResponseInvalid,
#         },
#     },
# )
# async def upload_document(
#     response: Response,
#     files: list[UploadFile] = FastAPIFile(...),
#     tags: Optional[list[str]] = None,
# ) -> AddDocumentResponse:
#     if any(
#         f
#         for f in files
#         if f.filename is None
#         or os.path.splitext(f.filename)[1][1:]
#         not in settings.SUPPORTED_UPLOAD_EXTENSIONS
#     ):
#         response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

#         return AddDocumentResponseInvalid(
#             message=f"Only files with the following extensions are supported: {', '.join(settings.SUPPORTED_UPLOAD_EXTENSIONS)}"
#         )

#     # TODO: read file here and generate UUID
#     content = await file.read()
#     await file.close()

#     # TODO: write file to disk (/temp/source/{file_id}.pdf)

#     # TODO: analyze file content for PII entities

#     # TODO: format tags

#     # TODO: format response

#     f = file

#     return AddDocumentResponseSuccess(
#         files=[
#             DocumentDto(
#                 id=f.id,
#                 filename=f.filename,
#                 blob_name=f.blob_name,
#                 created_at=f.created_at,
#                 tags=[DocumentTagDto(id=tag.id, name=tag.name) for tag in f.tags],
#                 pii_entities=f.pii_entities,
#             )
#         ]
#     )


# @documents_router.get("/{file_id}/metadata", response_model=DocumentDto)
# async def get_document_metadata(file_id: str) -> DocumentDto:
#     """Get metadata for a specific document. Same response as upload."""
#     # TODO: implement
#     return DocumentDto()


# @documents_router.post("/{file_id}/anonymize")
# async def anonymize_document(
#     file_id: str, request_body: DocumentAnonymizationRequest
# ) -> DocumentAnonymizationResponse:
#     """Anonymize a specific document."""
#     pass


# @documents_router.get("/{file_id}/download")
# async def download_document(
#     file_id: str, delete_from_server: bool = True
# ) -> FileResponse:
#     """Download a specific document.

#     Now we can use FastAPI's FileResponse to serve the file directly from disk;
#     however in the future, we may use StreamingResponse to stream large files (from memory or disk) to the client.
#     """
#     # TODO: find file by file_id, in /temp/ folder, read content and stream to client
#     confirmed_path = f"/temp/{file_id}.pdf"
#     confirmed_filename = f"{file_id}.pdf"

#     return FileResponse(path=confirmed_path, filename=confirmed_filename)
