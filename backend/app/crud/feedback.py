from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Board, Comment, FeedbackItem, FeedbackStatus, Vote
from app.schemas.feedback import CommentCreate, FeedbackItemCreate, FeedbackItemUpdate


def get_feedback_item(session: Session, item_id: UUID) -> FeedbackItem | None:
    return session.get(FeedbackItem, item_id)


def list_feedback_items(session: Session, board_id: UUID) -> list[FeedbackItem]:
    statement = (
        select(FeedbackItem)
        .where(FeedbackItem.board_id == board_id)
        .order_by(FeedbackItem.vote_count.desc(), FeedbackItem.created_at.desc())
    )
    return list(session.exec(statement).all())


def create_feedback_item(
    session: Session,
    board_id: UUID,
    item_in: FeedbackItemCreate,
    user_id: UUID | None = None,
    anonymous_token: str | None = None,
) -> FeedbackItem:
    item = FeedbackItem(
        board_id=board_id,
        title=item_in.title,
        description=item_in.description,
        category=item_in.category,
        author_id=user_id,
        author_name=item_in.author_name,
        author_email=item_in.author_email,
        anonymous_token=anonymous_token,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def update_feedback_item(
    session: Session, item: FeedbackItem, item_in: FeedbackItemUpdate
) -> FeedbackItem:
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    item.updated_at = datetime.now(UTC)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_feedback_item(session: Session, item: FeedbackItem) -> None:
    session.delete(item)
    session.commit()


def vote_feedback_item(
    session: Session,
    item: FeedbackItem,
    user_id: UUID | None = None,
    anonymous_token: str | None = None,
) -> bool:
    statement = select(Vote).where(
        Vote.feedback_item_id == item.id,
        (Vote.user_id == user_id) if user_id else (Vote.anonymous_token == anonymous_token),
    )
    existing = session.exec(statement).first()
    if existing:
        session.delete(existing)
        item.vote_count = max(0, item.vote_count - 1)
        session.add(item)
        session.commit()
        return False

    vote = Vote(
        feedback_item_id=item.id,
        user_id=user_id,
        anonymous_token=anonymous_token,
    )
    session.add(vote)
    item.vote_count += 1
    session.add(item)
    session.commit()
    return True


def create_comment(
    session: Session,
    item: FeedbackItem,
    comment_in: CommentCreate,
    user_id: UUID | None = None,
) -> Comment:
    comment = Comment(
        feedback_item_id=item.id,
        user_id=user_id,
        author_name=comment_in.author_name,
        content=comment_in.content,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def list_comments(session: Session, item_id: UUID) -> list[Comment]:
    statement = (
        select(Comment).where(Comment.feedback_item_id == item_id).order_by(Comment.created_at)
    )
    return list(session.exec(statement).all())


def get_comment_count(session: Session, item_id: UUID) -> int:
    statement = select(func.count(Comment.id)).where(Comment.feedback_item_id == item_id)
    return session.exec(statement).one() or 0


def list_roadmap_items(session: Session, workspace_id: UUID) -> list[FeedbackItem]:
    statement = (
        select(FeedbackItem)
        .join(Board, FeedbackItem.board_id == Board.id)
        .where(Board.workspace_id == workspace_id)
        .where(FeedbackItem.status != FeedbackStatus.CLOSED)
        .order_by(FeedbackItem.vote_count.desc(), FeedbackItem.created_at.desc())
    )
    return list(session.exec(statement).all())
