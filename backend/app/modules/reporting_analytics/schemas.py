"""Pydantic schemas for the Reporting & Analytics module."""

from pydantic import BaseModel, ConfigDict


class ReportingAnalyticsHealthResponse(BaseModel):
    """Health response for the Reporting & Analytics module."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    module: str
