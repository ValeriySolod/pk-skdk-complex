"""Pydantic schemas for the Integrations module API contract."""

from __future__ import annotations

from pydantic import BaseModel


class IntegrationsHealthRead(BaseModel):
    """Integrations module health response."""

    status: str
    module: str
