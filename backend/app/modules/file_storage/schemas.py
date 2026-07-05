from __future__ import annotations

from pydantic import BaseModel


class FileStorageHealthRead(BaseModel):
    status: str
