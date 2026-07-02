from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, DateTime, String, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class UserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class FeedbackStatus(StrEnum):
    UNDER_REVIEW = "under_review"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    SHIPPED = "shipped"
    CLOSED = "closed"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column(String(255), unique=True, index=True, nullable=False))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    full_name: str = Field(sa_column=Column(String(255), nullable=False))
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    workspaces: list["WorkspaceMember"] = Relationship(back_populates="user")
    feedback_items: list["FeedbackItem"] = Relationship(back_populates="author")
    votes: list["Vote"] = Relationship(back_populates="user")
    comments: list["Comment"] = Relationship(back_populates="author")


class Workspace(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(sa_column=Column(String(255), nullable=False))
    slug: str = Field(sa_column=Column(String(255), unique=True, index=True, nullable=False))
    description: str | None = Field(default=None, sa_column=Column(Text))
    is_public: bool = Field(default=True)
    owner_id: UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    owner: User = Relationship()
    members: list["WorkspaceMember"] = Relationship(back_populates="workspace")
    boards: list["Board"] = Relationship(back_populates="workspace")
    changelog_entries: list["ChangelogEntry"] = Relationship(back_populates="workspace")


class WorkspaceMember(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", nullable=False)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    role: UserRole = Field(sa_column=Column(String(50), nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    workspace: Workspace = Relationship(back_populates="members")
    user: User = Relationship(back_populates="workspaces")

    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="uix_workspace_user"),)


class Board(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", nullable=False)
    name: str = Field(sa_column=Column(String(255), nullable=False))
    slug: str = Field(sa_column=Column(String(255), nullable=False))
    description: str | None = Field(default=None, sa_column=Column(Text))
    category_options: list[str] = Field(
        default=["feature", "bug", "improvement", "integration"],
        sa_column=Column(JSON, nullable=False),
    )
    is_public: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    workspace: Workspace = Relationship(back_populates="boards")
    feedback_items: list["FeedbackItem"] = Relationship(back_populates="board")

    __table_args__ = (UniqueConstraint("workspace_id", "slug", name="uix_workspace_board_slug"),)


class FeedbackItem(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    board_id: UUID = Field(foreign_key="board.id", nullable=False)
    title: str = Field(sa_column=Column(String(500), nullable=False))
    description: str | None = Field(default=None, sa_column=Column(Text))
    category: str = Field(sa_column=Column(String(100), nullable=False))
    status: FeedbackStatus = Field(
        default=FeedbackStatus.UNDER_REVIEW, sa_column=Column(String(50), nullable=False)
    )
    vote_count: int = Field(default=0)
    author_id: UUID | None = Field(default=None, foreign_key="user.id")
    author_name: str | None = Field(default=None, sa_column=Column(String(255)))
    author_email: str | None = Field(default=None, sa_column=Column(String(255)))
    anonymous_token: str | None = Field(default=None, sa_column=Column(String(255), index=True))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    board: Board = Relationship(back_populates="feedback_items")
    author: User | None = Relationship(back_populates="feedback_items")
    votes: list["Vote"] = Relationship(back_populates="feedback_item")
    comments: list["Comment"] = Relationship(back_populates="feedback_item")


class Vote(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    feedback_item_id: UUID = Field(foreign_key="feedbackitem.id", nullable=False)
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    anonymous_token: str | None = Field(default=None, sa_column=Column(String(255), index=True))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    feedback_item: FeedbackItem = Relationship(back_populates="votes")
    user: User | None = Relationship(back_populates="votes")

    __table_args__ = (
        UniqueConstraint("feedback_item_id", "user_id", name="uix_feedback_user_vote"),
        UniqueConstraint("feedback_item_id", "anonymous_token", name="uix_feedback_anon_vote"),
    )


class Comment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    feedback_item_id: UUID = Field(foreign_key="feedbackitem.id", nullable=False)
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    author_name: str | None = Field(default=None, sa_column=Column(String(255)))
    content: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    feedback_item: FeedbackItem = Relationship(back_populates="comments")
    author: User | None = Relationship(back_populates="comments")


class ChangelogEntry(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", nullable=False)
    title: str = Field(sa_column=Column(String(500), nullable=False))
    content: str = Field(sa_column=Column(Text, nullable=False))
    shipped_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    feedback_item_id: UUID | None = Field(default=None, foreign_key="feedbackitem.id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    workspace: Workspace = Relationship(back_populates="changelog_entries")
    feedback_item: FeedbackItem | None = Relationship()
