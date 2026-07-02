from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChangelogEntryBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    content: str = Field(..., min_length=1)
    shipped_at: datetime | None = None
    feedback_item_id: UUID | None = None


class ChangelogEntryCreate(ChangelogEntryBase):
    pass


class ChangelogEntryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=500)
    content: str | None = Field(default=None, min_length=1)
    shipped_at: datetime | None = None
    feedback_item_id: UUID | None = None


class ChangelogEntryOut(ChangelogEntryBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
