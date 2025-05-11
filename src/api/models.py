from typing import List, Optional

from pydantic import BaseModel, Field

from src.api.config import settings


class AnalyzeRequest(BaseModel):
    text: str
    entities: Optional[List[str]] = Field(
        default_factory=lambda: ["PERSON", "LOCATION", "PHONE_NUMBER", "EMAIL", "IBAN"]
    )
    language: Optional[str] = settings.DEFAULT_LANGUAGE


class EntityResult(BaseModel):
    entity_type: str
    text: str
    start: int
    end: int
    score: float


class AnalyzeResponse(BaseModel):
    text: str
    entities_found: List[EntityResult]


class AnonymizeResponse(BaseModel):
    text: str
    anonymized: str
