import logging

from fastapi.routing import APIRouter

from src.api.routers.documents import documents_router

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def ping() -> dict[str, str]:
    """Health check endpoint.

    Geeft een eenvoudige status terug om te controleren of de API draait.
    """
    return {"ping": "pong"}


router.include_router(documents_router)
logging.info("Documents API router included!")


__all__ = ["router"]
