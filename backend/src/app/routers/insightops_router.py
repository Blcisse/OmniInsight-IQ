from fastapi import APIRouter


router = APIRouter(prefix="/insightops", tags=["InsightOps"])


@router.get("/health")
async def insightops_health() -> dict:
    return {"domain": "insightops-studio", "status": "ok"}
