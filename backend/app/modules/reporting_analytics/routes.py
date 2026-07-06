"""API routes for the Reporting & Analytics module."""

from fastapi import APIRouter

from .schemas import ReportingAnalyticsHealthResponse
from .service import ReportingAnalyticsService

router = APIRouter(prefix="/reporting-analytics", tags=["reporting-analytics"])


@router.get("/health", response_model=ReportingAnalyticsHealthResponse)
def reporting_analytics_health() -> ReportingAnalyticsHealthResponse:
    """Return Reporting & Analytics module health."""
    service = ReportingAnalyticsService()
    return ReportingAnalyticsHealthResponse(**service.health())
