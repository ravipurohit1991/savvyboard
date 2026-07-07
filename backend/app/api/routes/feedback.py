from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AnonTokenDep, CurrentUserDep, OptionalUserDep, SessionDep
from app.crud.board import get_board
from app.crud.feedback import (
    FeedbackSort,
    create_comment,
    create_feedback_item,
    delete_feedback_item,
    get_comment_count,
    get_feedback_item,
    list_comments,
    list_feedback_items,
    update_feedback_item,
    vote_feedback_item,
)
from app.models import FeedbackStatus
from app.schemas.feedback import (
    CommentCreate,
    CommentOut,
    FeedbackItemAuthorOut,
    FeedbackItemCreate,
    FeedbackItemOut,
    FeedbackItemUpdate,
    VoteCreate,
)

router = APIRouter(
    prefix="/workspaces/{workspace_id}/boards/{board_id}/feedback", tags=["feedback"]
)


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


@router.get("/", response_model=list[FeedbackItemOut])
def list_feedback(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    current_user: OptionalUserDep,
    anon_token: AnonTokenDep,
    search: str | None = Query(default=None, min_length=1, max_length=200),
    category: str | None = Query(default=None, min_length=1, max_length=100),
    status: FeedbackStatus | None = Query(default=None),
    sort: FeedbackSort = Query(default=FeedbackSort.TOP_VOTED),
) -> Any:
    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    items = list_feedback_items(
        session,
        board_id,
        search=search,
        category=category,
        status=status,
        sort=sort,
    )
    return [
        _serialize_item(item, current_user.id if current_user else None, anon_token, session)
        for item in items
    ]


@router.post("/", response_model=FeedbackItemOut, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    item_in: FeedbackItemCreate,
    current_user: OptionalUserDep,
    anon_token: AnonTokenDep,
) -> Any:
    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    if not board.is_public and not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    item = create_feedback_item(
        session,
        board_id,
        item_in,
        user_id=current_user.id if current_user else None,
        anonymous_token=anon_token,
    )
    return _serialize_item(item, current_user.id if current_user else None, anon_token, session)


@router.get("/{item_id}", response_model=FeedbackItemOut)
def read_feedback_item(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    item_id: UUID,
    current_user: OptionalUserDep,
    anon_token: AnonTokenDep,
) -> Any:
    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    item = get_feedback_item(session, item_id)
    if not item or item.board_id != board_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return _serialize_item(item, current_user.id if current_user else None, anon_token, session)


@router.patch("/{item_id}", response_model=FeedbackItemOut)
def patch_feedback_item(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    item_id: UUID,
    item_in: FeedbackItemUpdate,
    current_user: CurrentUserDep,
    anon_token: AnonTokenDep,
) -> Any:
    from app.crud.workspace import get_member_role

    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    role = get_member_role(session, workspace_id, current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a workspace member")
    item = get_feedback_item(session, item_id)
    if not item or item.board_id != board_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    item = update_feedback_item(session, item, item_in)
    return _serialize_item(item, current_user.id, anon_token, session)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_feedback_item(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    item_id: UUID,
    current_user: CurrentUserDep,
) -> None:
    from app.crud.workspace import get_member_role

    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    role = get_member_role(session, workspace_id, current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a workspace member")
    item = get_feedback_item(session, item_id)
    if not item or item.board_id != board_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    delete_feedback_item(session, item)


@router.post("/{item_id}/vote", response_model=FeedbackItemOut)
def vote(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    item_id: UUID,
    current_user: OptionalUserDep,
    anon_token: AnonTokenDep,
    vote_in: VoteCreate | None = None,
) -> Any:
    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    item = get_feedback_item(session, item_id)
    if not item or item.board_id != board_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    token = anon_token
    if vote_in and vote_in.anonymous_token:
        token = vote_in.anonymous_token
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


@router.get("/{item_id}/comments", response_model=list[CommentOut])
def read_comments(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    item_id: UUID,
) -> Any:
    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    item = get_feedback_item(session, item_id)
    if not item or item.board_id != board_id:
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


@router.post("/{item_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def post_comment(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    item_id: UUID,
    comment_in: CommentCreate,
    current_user: OptionalUserDep,
) -> Any:
    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    item = get_feedback_item(session, item_id)
    if not item or item.board_id != board_id:
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
