from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import UserRole


class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    is_public: bool = True


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_public: bool | None = None


class WorkspaceMemberOut(BaseModel):
    id: UUID
    user_id: UUID
    role: UserRole
    email: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class WorkspaceOut(WorkspaceBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceDetailOut(WorkspaceOut):
    members: list[WorkspaceMemberOut]

    model_config = ConfigDict(from_attributes=True)
