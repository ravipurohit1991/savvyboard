from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, SessionDep
from app.crud.board import (
    create_board,
    delete_board,
    get_board,
    get_board_by_slug,
    list_boards_by_workspace,
    update_board,
)
from app.crud.workspace import get_member_role, get_workspace
from app.models import UserRole
from app.schemas.board import BoardCreate, BoardOut, BoardUpdate

router = APIRouter(prefix="/workspaces/{workspace_id}/boards", tags=["boards"])


def _can_manage(session: SessionDep, workspace_id: UUID, user_id: UUID) -> bool:
    role = get_member_role(session, workspace_id, user_id)
    return role in (UserRole.OWNER, UserRole.ADMIN)


@router.get("/", response_model=list[BoardOut])
def list_boards(
    session: SessionDep,
    workspace_id: UUID,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    role = get_member_role(session, workspace_id, current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a workspace member")
    return list_boards_by_workspace(session, workspace_id)


@router.post("/", response_model=BoardOut, status_code=status.HTTP_201_CREATED)
def create_new_board(
    session: SessionDep,
    workspace_id: UUID,
    board_in: BoardCreate,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if not _can_manage(session, workspace_id, current_user.id) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    existing = get_board_by_slug(session, workspace_id, board_in.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Board slug already in use"
        )
    board = create_board(session, workspace_id, board_in)
    return board


@router.get("/{board_id}", response_model=BoardOut)
def read_board(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    role = get_member_role(session, workspace_id, current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a workspace member")
    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board


@router.patch("/{board_id}", response_model=BoardOut)
def patch_board(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    board_in: BoardUpdate,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if not _can_manage(session, workspace_id, current_user.id) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    board = update_board(session, board, board_in)
    return board


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_board(
    session: SessionDep,
    workspace_id: UUID,
    board_id: UUID,
    current_user: CurrentUserDep,
) -> None:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if not _can_manage(session, workspace_id, current_user.id) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    board = get_board(session, board_id)
    if not board or board.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    delete_board(session, board)
