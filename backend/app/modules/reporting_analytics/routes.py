"""API routes for the Reporting & Analytics module."""

from fastapi import APIRouter

from .schemas import ReportingAnalyticsHealthResponse

router = APIRouter()


@router.get("/health", response_model=ReportingAnalyticsHealthResponse)
def reporting_analytics_health() -> ReportingAnalyticsHealthResponse:
    """Return Reporting & Analytics module health."""
    return ReportingAnalyticsHealthResponse(
        status="healthy",
        module="reporting_analytics",
    )
