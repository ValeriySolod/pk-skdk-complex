"""Pydantic schemas for the Administration module."""

from __future__ import annotations

from pydantic import BaseModel


class AdministrationHealthRead(BaseModel):
    """Health response for the Administration module."""

    status: str
