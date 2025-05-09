import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from pydantic import BaseModel
from anonymizer.engine import ModularTextAnalyzer
from typing import List, Optional

app = FastAPI(title="Presidio-NL API", description="API voor Nederlandse tekst analyse en anonimisatie", version="0.2.0")

analyzer = ModularTextAnalyzer()

class AnalyzeRequest(BaseModel):
    text: str
    entities: Optional[List[str]] = None
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

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest):
    results = analyzer.analyze_text(request.text, request.entities, request.language)
    entities_found = [
        EntityResult(
            entity_type=ent["entity_type"],
            text=ent["text"],
            start=ent["start"],
            end=ent["end"],
            score=ent["score"]
        ) for ent in results
    ]
    return AnalyzeResponse(text=request.text, entities_found=entities_found)

@app.post("/anonymize", response_model=AnonymizeResponse)
def anonymize_text(request: AnalyzeRequest):
    anonymized = analyzer.anonymize_text(request.text, request.entities, request.language)
    return AnonymizeResponse(text=request.text, anonymized=anonymized) 