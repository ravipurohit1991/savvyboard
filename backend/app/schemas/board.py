from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BoardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    category_options: list[str] = Field(default=["feature", "bug", "improvement", "integration"])
    is_public: bool = True


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category_options: list[str] | None = None
    is_public: bool | None = None


class BoardOut(BoardBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
