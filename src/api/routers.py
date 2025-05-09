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
    return {"ping": "pong"}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    results = analyzer.analyze_text(request.text, request.entities, request.language)
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
    anonymized = analyzer.anonymize_text(
        request.text, request.entities, request.language
    )
    return AnonymizeResponse(text=request.text, anonymized=anonymized)
