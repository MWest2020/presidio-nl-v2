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


class DocumentAnonymizationRequest(BaseModel):
    pii_entities_to_anonymize: list[str]  # List of PII entities to anonymize


class DocumentAnonymizationResponse(BaseModel):
    id: str
    filename: str
    anonymized_at: datetime
    time_taken: int  # Time taken for anonymization in seconds
    status: str  # e.g., "success", "failed"
    pii_entities: Optional[list[dict[str, str]]] = (
        None  # Anonymized entities if applicable
    )
