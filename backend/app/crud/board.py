from uuid import UUID

from sqlmodel import Session, select

from app.models import Board
from app.schemas.board import BoardCreate, BoardUpdate


def get_board(session: Session, board_id: UUID) -> Board | None:
    return session.get(Board, board_id)


def get_board_by_slug(session: Session, workspace_id: UUID, slug: str) -> Board | None:
    statement = select(Board).where(Board.workspace_id == workspace_id, Board.slug == slug)
    return session.exec(statement).first()


def list_boards_by_workspace(session: Session, workspace_id: UUID) -> list[Board]:
    statement = select(Board).where(Board.workspace_id == workspace_id).order_by(Board.created_at)
    return list(session.exec(statement).all())


def create_board(session: Session, workspace_id: UUID, board_create: BoardCreate) -> Board:
    board = Board(
        workspace_id=workspace_id,
        name=board_create.name,
        slug=board_create.slug,
        description=board_create.description,
        category_options=board_create.category_options,
        is_public=board_create.is_public,
    )
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


def update_board(session: Session, board: Board, board_update: BoardUpdate) -> Board:
    update_data = board_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(board, field, value)
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


def delete_board(session: Session, board: Board) -> None:
    session.delete(board)
    session.commit()
