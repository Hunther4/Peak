from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Endpoint simple para el semáforo del frontend."""
    return {"status": "ok"}
