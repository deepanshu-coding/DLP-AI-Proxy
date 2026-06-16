from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import MetricsResponse
from app.services.metrics_service import metrics

router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """Return aggregated request counters."""
    return metrics.snapshot()
