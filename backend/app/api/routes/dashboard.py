from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.crud.workspace import get_member_role, get_workspace
from app.models import Board, ChangelogEntry, Comment, FeedbackItem, Vote, WorkspaceMember

router = APIRouter(prefix="/workspaces/{workspace_id}/dashboard", tags=["dashboard"])


@router.get("/metrics")
def read_metrics(
    session: SessionDep,
    workspace_id: UUID,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    role = get_member_role(session, workspace_id, current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not a workspace member")

    board_ids_sub = select(Board.id).where(Board.workspace_id == workspace_id).scalar_subquery()
    feedback_ids_sub = (
        select(FeedbackItem.id).where(FeedbackItem.board_id.in_(board_ids_sub)).scalar_subquery()
    )

    total_feedback = (
        session.exec(
            select(func.count(FeedbackItem.id)).where(FeedbackItem.board_id.in_(board_ids_sub))
        ).one()
        or 0
    )
    total_votes = (
        session.exec(
            select(func.count(Vote.id)).where(Vote.feedback_item_id.in_(feedback_ids_sub))
        ).one()
        or 0
    )
    total_comments = (
        session.exec(
            select(func.count(Comment.id)).where(Comment.feedback_item_id.in_(feedback_ids_sub))
        ).one()
        or 0
    )
    shipped_count = (
        session.exec(
            select(func.count(ChangelogEntry.id)).where(ChangelogEntry.workspace_id == workspace_id)
        ).one()
        or 0
    )
    members_count = (
        session.exec(
            select(func.count(WorkspaceMember.id)).where(
                WorkspaceMember.workspace_id == workspace_id
            )
        ).one()
        or 0
    )

    category_counts = {}
    rows = session.exec(
        select(FeedbackItem.category, func.count(FeedbackItem.id))
        .where(FeedbackItem.board_id.in_(board_ids_sub))
        .group_by(FeedbackItem.category)
    ).all()
    for category, count in rows:
        category_counts[category] = count

    top_items_rows = session.exec(
        select(FeedbackItem)
        .where(FeedbackItem.board_id.in_(board_ids_sub))
        .order_by(FeedbackItem.vote_count.desc())
        .limit(5)
    ).all()
    top_items = [
        {
            "id": str(item.id),
            "title": item.title,
            "vote_count": item.vote_count,
            "category": item.category,
        }
        for item in top_items_rows
    ]

    return {
        "total_feedback": total_feedback,
        "total_votes": total_votes,
        "total_comments": total_comments,
        "shipped_count": shipped_count,
        "members_count": members_count,
        "category_counts": category_counts,
        "top_items": top_items,
    }
