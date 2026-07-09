"""Pydantic schemas for the Monitoring & Health module API contract."""

from __future__ import annotations

from pydantic import BaseModel


class MonitoringHealthHealthRead(BaseModel):
    """Monitoring & Health module health response."""

    status: str
    module: str
