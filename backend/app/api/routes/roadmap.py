from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import AnonTokenDep, OptionalUserDep, SessionDep
from app.crud.feedback import list_roadmap_items
from app.crud.workspace import get_member_role, get_workspace
from app.models import FeedbackStatus
from app.schemas.feedback import FeedbackItemAuthorOut, FeedbackItemOut, RoadmapColumnOut

router = APIRouter(prefix="/workspaces/{workspace_id}/roadmap", tags=["roadmap"])


ROADMAP_COLUMNS = [
    (FeedbackStatus.UNDER_REVIEW, "Under Review"),
    (FeedbackStatus.PLANNED, "Planned"),
    (FeedbackStatus.IN_PROGRESS, "In Progress"),
    (FeedbackStatus.SHIPPED, "Shipped"),
]


def _build_author(item: Any) -> FeedbackItemAuthorOut:
    if item.author_id:
        return FeedbackItemAuthorOut(
            id=item.author_id, name=item.author.full_name if item.author else None
        )
    return FeedbackItemAuthorOut(id=None, name=item.author_name or "Anonymous")


def _serialize_item(item: Any, user_id: UUID | None, anon_token: str | None) -> FeedbackItemOut:
    user_voted = False
    if user_id:
        user_voted = any(v.user_id == user_id for v in item.votes)
    elif anon_token:
        user_voted = any(v.anonymous_token == anon_token for v in item.votes)
    return FeedbackItemOut(
        id=item.id,
        board_id=item.board_id,
        title=item.title,
        description=item.description,
        category=item.category,
        status=item.status,
        vote_count=item.vote_count,
        user_voted=user_voted,
        author=_build_author(item),
        comment_count=len(item.comments) if item.comments else 0,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/", response_model=list[RoadmapColumnOut])
def read_workspace_roadmap(
    session: SessionDep,
    workspace_id: UUID,
    current_user: OptionalUserDep,
    anon_token: AnonTokenDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if not workspace.is_public:
        role = current_user and get_member_role(session, workspace_id, current_user.id)
        if not role and not (current_user and current_user.is_superuser):
            raise HTTPException(status_code=403, detail="Workspace is private")
    items = list_roadmap_items(session, workspace_id)
    user_id = current_user.id if current_user else None
    serialized = [_serialize_item(item, user_id, anon_token) for item in items]
    grouped: dict[FeedbackStatus, list[FeedbackItemOut]] = {
        status: [] for status, _ in ROADMAP_COLUMNS
    }
    for item in serialized:
        if item.status in grouped:
            grouped[item.status].append(item)
    return [
        RoadmapColumnOut(status=status, label=label, items=grouped[status])
        for status, label in ROADMAP_COLUMNS
    ]
