from __future__ import annotations

from pydantic import BaseModel


class NotificationsHealthRead(BaseModel):
    status: str
