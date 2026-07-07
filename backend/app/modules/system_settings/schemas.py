"""Pydantic schemas for the System Settings module API contract."""

from __future__ import annotations

from pydantic import BaseModel


class SystemSettingsHealthRead(BaseModel):
    status: str
