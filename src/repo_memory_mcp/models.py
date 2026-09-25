from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, field_validator

MemoryType = Literal["correction", "rule", "architecture", "bugfix", "convention", "constraint", "preference", "decision"]
MemoryStatus = Literal["active", "archived"]
Importance = Literal["low", "normal", "high", "critical"]

class Memory(BaseModel):
    id: str
    repository_id: str
    repository_path: str
    memory_type: MemoryType
    topic: str = Field(min_length=1, max_length=240)
    content: str = Field(min_length=1, max_length=20000)
    context_file: str = Field(default="general", max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=30)
    importance: Importance = "normal"
    status: MemoryStatus = "active"
    source: str = "mcp"
    created_at: datetime
    updated_at: datetime

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, values: list[str]) -> list[str]:
        return sorted({v.strip().lower() for v in values if v and v.strip()})

    @classmethod
    def now(cls) -> datetime:
        return datetime.now(timezone.utc)
