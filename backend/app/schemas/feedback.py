from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import FeedbackStatus


class FeedbackItemBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: str | None = None
    category: str = Field(..., min_length=1, max_length=100)


class FeedbackItemCreate(FeedbackItemBase):
    author_name: str | None = Field(default=None, max_length=255)
    author_email: str | None = Field(default=None, max_length=255)


class FeedbackItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=500)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    status: FeedbackStatus | None = None


class FeedbackItemAuthorOut(BaseModel):
    id: UUID | None = None
    name: str | None = None


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    author_name: str | None = Field(default=None, max_length=255)


class CommentOut(BaseModel):
    id: UUID
    content: str
    author: FeedbackItemAuthorOut
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackItemOut(FeedbackItemBase):
    id: UUID
    board_id: UUID
    status: FeedbackStatus
    vote_count: int
    user_voted: bool
    author: FeedbackItemAuthorOut
    comment_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VoteCreate(BaseModel):
    anonymous_token: str | None = None


class RoadmapColumnOut(BaseModel):
    status: FeedbackStatus
    label: str
    items: list[FeedbackItemOut]
