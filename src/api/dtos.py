from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from src.api.config import settings


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

    @field_validator("pii_entities_to_anonymize")
    def validate_pii_entities(cls, value: list[str]) -> list[str]:
        """Check if the PII entities are in list settings.SUPPORTED_PII_ENTITIES_TO_ANONYMIZE."""
        unsupported_entities = [
            entity
            for entity in value
            if entity not in settings.SUPPORTED_PII_ENTITIES_TO_ANONYMIZE
        ]
        if unsupported_entities:
            raise ValueError(
                f"Unsupported PII entities: {', '.join(unsupported_entities)}. "
                f"Supported entities are: {', '.join(settings.SUPPORTED_PII_ENTITIES_TO_ANONYMIZE)}"
            )
        return value


class DocumentAnonymizationResponse(BaseModel):
    id: str
    filename: str
    anonymized_at: datetime
    time_taken: int  # Time taken for anonymization in seconds
    status: str  # e.g., "success", "failed"
    pii_entities: Optional[list[dict[str, str]]] = (
        None  # Anonymized entities if applicable
    )
