from typing import List, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str
    entities: Optional[List[str]] = Field(
        default_factory=lambda: ["PERSON", "LOCATION", "PHONE_NUMBER", "EMAIL", "IBAN"]
    )
    language: Optional[str] = "nl"


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
