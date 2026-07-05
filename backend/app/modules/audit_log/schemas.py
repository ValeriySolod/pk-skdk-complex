from __future__ import annotations

from pydantic import BaseModel


class AuditLogHealthRead(BaseModel):
    status: str
