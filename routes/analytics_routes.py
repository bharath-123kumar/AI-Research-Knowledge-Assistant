from fastapi import APIRouter
from src.analytics.metrics import AnalyticsEngine

router = APIRouter(prefix="/analytics", tags=["System Analytics"])

@router.get("/dashboard")
async def get_dashboard_metrics():
    """Returns total documents, chunks, query analytics, and classification category distribution."""
    metrics = AnalyticsEngine.get_dashboard_analytics()
    return metrics
