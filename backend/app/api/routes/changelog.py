from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, SessionDep
from app.crud.changelog import (
    create_changelog_entry,
    delete_changelog_entry,
    get_changelog_entry,
    list_changelog_entries,
    update_changelog_entry,
)
from app.crud.workspace import get_member_role, get_workspace
from app.models import UserRole
from app.schemas.changelog import ChangelogEntryCreate, ChangelogEntryOut, ChangelogEntryUpdate

router = APIRouter(prefix="/workspaces/{workspace_id}/changelog", tags=["changelog"])


def _can_manage(session: SessionDep, workspace_id: UUID, user_id: UUID) -> bool:
    role = get_member_role(session, workspace_id, user_id)
    return role in (UserRole.OWNER, UserRole.ADMIN)


@router.get("/", response_model=list[ChangelogEntryOut])
def list_entries(
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
    return list_changelog_entries(session, workspace_id)


@router.post("/", response_model=ChangelogEntryOut, status_code=status.HTTP_201_CREATED)
def create_entry(
    session: SessionDep,
    workspace_id: UUID,
    entry_in: ChangelogEntryCreate,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if not _can_manage(session, workspace_id, current_user.id) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return create_changelog_entry(session, workspace_id, entry_in)


@router.get("/{entry_id}", response_model=ChangelogEntryOut)
def read_entry(
    session: SessionDep,
    workspace_id: UUID,
    entry_id: UUID,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    role = get_member_role(session, workspace_id, current_user.id)
    if not role and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a workspace member")
    entry = get_changelog_entry(session, entry_id)
    if not entry or entry.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return entry


@router.patch("/{entry_id}", response_model=ChangelogEntryOut)
def patch_entry(
    session: SessionDep,
    workspace_id: UUID,
    entry_id: UUID,
    entry_in: ChangelogEntryUpdate,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if not _can_manage(session, workspace_id, current_user.id) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    entry = get_changelog_entry(session, entry_id)
    if not entry or entry.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return update_changelog_entry(session, entry, entry_in)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_entry(
    session: SessionDep,
    workspace_id: UUID,
    entry_id: UUID,
    current_user: CurrentUserDep,
) -> None:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if not _can_manage(session, workspace_id, current_user.id) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    entry = get_changelog_entry(session, entry_id)
    if not entry or entry.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    delete_changelog_entry(session, entry)
