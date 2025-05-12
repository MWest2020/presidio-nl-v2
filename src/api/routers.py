import logging

from fastapi import HTTPException
from fastapi.routing import APIRouter

from src.api.anonymizer.engine import ModularTextAnalyzer
from src.api.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnonymizeResponse,
    EntityResult,
)

router = APIRouter()
analyzer = ModularTextAnalyzer()


@router.get("/health")
def ping() -> dict[str, str]:
    """
    Health check endpoint.
    Geeft een eenvoudige status terug om te controleren of de API draait.
    """
    return {"ping": "pong"}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyseer tekst op PII-entiteiten via de ModularTextAnalyzer.

    Args:
        request (AnalyzeRequest): Request met tekst, entiteiten en taal.

    Returns:
        AnalyzeResponse: Response met gevonden entiteiten in de tekst.
    """
    try:
        results = analyzer.analyze_text(
            request.text, request.entities, request.language
        )
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during text analysis. Please try again later.",
        )

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


@router.post("/anonymize", response_model=AnonymizeResponse)
def anonymize_text(request: AnalyzeRequest) -> AnonymizeResponse:
    """
    Anonimiseer tekst door gevonden PII te vervangen door placeholders.

    Args:
        request (AnalyzeRequest): Request met tekst, entiteiten en taal.

    Returns:
        AnonymizeResponse: Response met originele en geanonimiseerde tekst.
    """
    anonymized = analyzer.anonymize_text(
        request.text, request.entities, request.language
    )
    return AnonymizeResponse(text=request.text, anonymized=anonymized)
