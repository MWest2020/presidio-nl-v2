from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import settings, setup_logging
from src.api.routers import router

setup_logging()

app = FastAPI(
    title="Presidio-NL API",
    description="API voor Nederlandse tekst analyse en anonimisatie",
    version="0.3.0",
    docs_url="/api/v1/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)
