from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.api.anonymizer.engine import ModularTextAnalyzer
from src.api.config import setup_logging
from src.api.routers import router

setup_logging()

app = FastAPI(
    title="Presidio-NL API",
    description="API voor Nederlandse tekst analyse en anonimisatie",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)

analyzer = ModularTextAnalyzer()

SUPPORTED_ENTITIES = ["PERSON", "LOCATION", "PHONE_NUMBER", "EMAIL", "IBAN"]


@app.get("/entities")
def get_supported_entities() -> dict:
    """Endpoint om de lijst van ondersteunde entiteitstypen op te vragen.

    Returns:
        dict: Dictionary met een lijst van ondersteunde entiteiten.
    """
    return {"supported_entities": SUPPORTED_ENTITIES}


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


@app.get("/health")
def ping() -> dict[str, str]:
    """Health check endpoint.

    Geeft een eenvoudige status terug om te controleren of de API draait.
    """
    return {"ping": "pong"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyseer tekst op PII-entiteiten via de ModularTextAnalyzer.

    Args:
        request (AnalyzeRequest): Request met tekst, entiteiten en taal.

    Returns:
        AnalyzeResponse: Response met gevonden entiteiten in de tekst.
    """
    try:
        results = analyzer.analyze_text(
            request.text,
            request.entities,  # type: ignore
            request.language,  # type: ignore
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    entities_found = [
        EntityResult(
            entity_type=ent["entity_type"],
            text=ent["text"],
            start=ent["start"],
            end=ent["end"],
            score=ent["score"],
        )
        for ent in results
    ]
    return AnalyzeResponse(text=request.text, entities_found=entities_found)


@app.post("/anonymize", response_model=AnonymizeResponse)
def anonymize_text(request: AnalyzeRequest) -> AnonymizeResponse:
    """Anonimiseer tekst door gevonden PII te vervangen door placeholders.

    Args:
        request (AnalyzeRequest): Request met tekst, entiteiten en taal.

    Returns:
        AnonymizeResponse: Response met originele en geanonimiseerde tekst.
    """
    try:
        anonymized = analyzer.anonymize_text(
            request.text,
            request.entities,  # type: ignore
            request.language,  # type: ignore
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return AnonymizeResponse(text=request.text, anonymized=anonymized)
