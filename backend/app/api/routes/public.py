from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import AnonTokenDep, OptionalUserDep, SessionDep
from app.crud.board import get_board_by_slug, list_boards_by_workspace
from app.crud.changelog import list_changelog_entries
from app.crud.feedback import (
    create_comment,
    create_feedback_item,
    get_comment_count,
    get_feedback_item,
    list_comments,
    list_feedback_items,
    vote_feedback_item,
)
from app.crud.workspace import get_workspace_by_slug
from app.models import FeedbackStatus
from app.schemas.board import BoardOut
from app.schemas.changelog import ChangelogEntryOut
from app.schemas.feedback import (
    CommentCreate,
    CommentOut,
    FeedbackItemAuthorOut,
    FeedbackItemCreate,
    FeedbackItemOut,
    RoadmapColumnOut,
    VoteCreate,
)
from app.schemas.workspace import WorkspaceOut

router = APIRouter(prefix="/public", tags=["public"])


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


def _serialize_item(
    item: Any, user_id: UUID | None, anon_token: str | None, session: SessionDep
) -> FeedbackItemOut:
    user_voted = False
    if user_id:
        user_voted = any(v.user_id == user_id for v in item.votes)
    elif anon_token:
        user_voted = any(v.anonymous_token == anon_token for v in item.votes)
    comment_count = len(item.comments) if item.comments else get_comment_count(session, item.id)
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
        comment_count=comment_count,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/workspaces/{slug}")
def read_public_workspace(session: SessionDep, slug: str) -> Any:
    workspace = get_workspace_by_slug(session, slug)
    if not workspace or not workspace.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    boards = list_boards_by_workspace(session, workspace.id)
    return {
        "workspace": WorkspaceOut.model_validate(workspace),
        "boards": [BoardOut.model_validate(b) for b in boards if b.is_public],
    }


@router.get("/workspaces/{slug}/feedback/{board_slug}", response_model=list[FeedbackItemOut])
def list_public_feedback(
    session: SessionDep,
    slug: str,
    board_slug: str,
    current_user: OptionalUserDep,
    anon_token: AnonTokenDep,
) -> Any:
    workspace = get_workspace_by_slug(session, slug)
    if not workspace or not workspace.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    board = get_board_by_slug(session, workspace.id, board_slug)
    if not board or not board.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    items = list_feedback_items(session, board.id)
    return [
        _serialize_item(item, current_user.id if current_user else None, anon_token, session)
        for item in items
    ]


@router.post(
    "/workspaces/{slug}/feedback/{board_slug}",
    response_model=FeedbackItemOut,
    status_code=status.HTTP_201_CREATED,
)
def submit_public_feedback(
    session: SessionDep,
    slug: str,
    board_slug: str,
    item_in: FeedbackItemCreate,
    current_user: OptionalUserDep,
    anon_token: AnonTokenDep,
) -> Any:
    workspace = get_workspace_by_slug(session, slug)
    if not workspace or not workspace.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    board = get_board_by_slug(session, workspace.id, board_slug)
    if not board or not board.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    item = create_feedback_item(
        session,
        board.id,
        item_in,
        user_id=current_user.id if current_user else None,
        anonymous_token=anon_token,
    )
    return _serialize_item(item, current_user.id if current_user else None, anon_token, session)


@router.post(
    "/workspaces/{slug}/feedback/{board_slug}/{item_id}/vote", response_model=FeedbackItemOut
)
def vote_public_feedback(
    session: SessionDep,
    slug: str,
    board_slug: str,
    item_id: UUID,
    current_user: OptionalUserDep,
    anon_token: AnonTokenDep,
    vote_in: VoteCreate | None = None,
) -> Any:
    workspace = get_workspace_by_slug(session, slug)
    if not workspace or not workspace.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    board = get_board_by_slug(session, workspace.id, board_slug)
    if not board or not board.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    item = get_feedback_item(session, item_id)
    if not item or item.board_id != board.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    token = anon_token or (vote_in.anonymous_token if vote_in else None)
    if not current_user and not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Anonymous token required"
        )
    vote_feedback_item(
        session,
        item,
        user_id=current_user.id if current_user else None,
        anonymous_token=token if not current_user else None,
    )
    session.refresh(item)
    return _serialize_item(item, current_user.id if current_user else None, token, session)


@router.get(
    "/workspaces/{slug}/feedback/{board_slug}/{item_id}/comments", response_model=list[CommentOut]
)
def read_public_comments(
    session: SessionDep,
    slug: str,
    board_slug: str,
    item_id: UUID,
) -> Any:
    workspace = get_workspace_by_slug(session, slug)
    if not workspace or not workspace.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    board = get_board_by_slug(session, workspace.id, board_slug)
    if not board or not board.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    item = get_feedback_item(session, item_id)
    if not item or item.board_id != board.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    comments = list_comments(session, item_id)
    return [
        CommentOut(
            id=c.id,
            content=c.content,
            author=FeedbackItemAuthorOut(
                id=c.user_id,
                name=c.author.full_name if c.author else (c.author_name or "Anonymous"),
            ),
            created_at=c.created_at,
        )
        for c in comments
    ]


@router.post(
    "/workspaces/{slug}/feedback/{board_slug}/{item_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def post_public_comment(
    session: SessionDep,
    slug: str,
    board_slug: str,
    item_id: UUID,
    comment_in: CommentCreate,
    current_user: OptionalUserDep,
) -> Any:
    workspace = get_workspace_by_slug(session, slug)
    if not workspace or not workspace.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    board = get_board_by_slug(session, workspace.id, board_slug)
    if not board or not board.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    item = get_feedback_item(session, item_id)
    if not item or item.board_id != board.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    comment = create_comment(
        session,
        item,
        comment_in,
        user_id=current_user.id if current_user else None,
    )
    return CommentOut(
        id=comment.id,
        content=comment.content,
        author=FeedbackItemAuthorOut(
            id=comment.user_id,
            name=(
                comment.author.full_name if comment.author else (comment.author_name or "Anonymous")
            ),
        ),
        created_at=comment.created_at,
    )


@router.get("/workspaces/{slug}/roadmap", response_model=list[RoadmapColumnOut])
def read_public_roadmap(
    session: SessionDep,
    slug: str,
    current_user: OptionalUserDep,
    anon_token: AnonTokenDep,
) -> Any:
    from app.crud.feedback import list_roadmap_items

    workspace = get_workspace_by_slug(session, slug)
    if not workspace or not workspace.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    items = list_roadmap_items(session, workspace.id)
    user_id = current_user.id if current_user else None
    serialized = [_serialize_item(item, user_id, anon_token, session) for item in items]
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


@router.get("/workspaces/{slug}/changelog", response_model=list[ChangelogEntryOut])
def read_public_changelog(session: SessionDep, slug: str) -> Any:
    workspace = get_workspace_by_slug(session, slug)
    if not workspace or not workspace.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return list_changelog_entries(session, workspace.id)
