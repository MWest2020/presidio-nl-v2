from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentTagDto(BaseModel):
    id: str
    name: str


class DocumentDto(BaseModel):
    id: str
    filename: str
    content_type: str
    uploaded_at: datetime
    tags: list[DocumentTagDto]
    pii_entities: Optional[list[dict[str, str]]] = None


class AddDocumentResponseInvalid(BaseModel):
    message: str


class AddDocumentResponseSuccess(BaseModel):
    files: list[DocumentDto]


AddDocumentResponse = AddDocumentResponseSuccess | AddDocumentResponseInvalid
