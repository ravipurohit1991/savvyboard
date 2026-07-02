from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, SessionDep
from app.crud.workspace import (
    add_workspace_member,
    create_workspace,
    delete_workspace,
    get_member_role,
    get_workspace,
    get_workspace_by_slug,
    get_workspace_members,
    list_workspaces_for_user,
    remove_workspace_member,
    update_member_role,
    update_workspace,
)
from app.models import UserRole
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceDetailOut,
    WorkspaceMemberOut,
    WorkspaceOut,
    WorkspaceUpdate,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def _serialize_members(members: list[tuple[Any, Any]]) -> list[WorkspaceMemberOut]:
    return [
        WorkspaceMemberOut(
            id=member.id,
            user_id=user.id,
            role=member.role,
            email=user.email,
            full_name=user.full_name,
        )
        for member, user in members
    ]


@router.get("/", response_model=list[WorkspaceOut])
def list_my_workspaces(session: SessionDep, current_user: CurrentUserDep) -> Any:
    return list_workspaces_for_user(session, current_user.id)


@router.post("/", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
def create_new_workspace(
    session: SessionDep,
    current_user: CurrentUserDep,
    workspace_in: WorkspaceCreate,
) -> Any:
    existing = get_workspace_by_slug(session, workspace_in.slug)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already in use")
    workspace = create_workspace(session, workspace_in, current_user.id)
    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceDetailOut)
def read_workspace(
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
    members = get_workspace_members(session, workspace_id)
    return WorkspaceDetailOut(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        description=workspace.description,
        is_public=workspace.is_public,
        owner_id=workspace.owner_id,
        created_at=workspace.created_at,
        members=_serialize_members(members),
    )


@router.patch("/{workspace_id}", response_model=WorkspaceOut)
def patch_workspace(
    session: SessionDep,
    workspace_id: UUID,
    workspace_in: WorkspaceUpdate,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    role = get_member_role(session, workspace_id, current_user.id)
    if (not role or role not in (UserRole.OWNER, UserRole.ADMIN)) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    workspace = update_workspace(session, workspace, workspace_in)
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_workspace(
    session: SessionDep,
    workspace_id: UUID,
    current_user: CurrentUserDep,
) -> None:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    role = get_member_role(session, workspace_id, current_user.id)
    if role != UserRole.OWNER and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can delete a workspace"
        )
    delete_workspace(session, workspace)


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberOut)
def add_member(
    session: SessionDep,
    workspace_id: UUID,
    email: str,
    role: UserRole,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    current_role = get_member_role(session, workspace_id, current_user.id)
    if (
        not current_role or current_role not in (UserRole.OWNER, UserRole.ADMIN)
    ) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    from app.crud.user import get_user_by_email

    user = get_user_by_email(session, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    existing_role = get_member_role(session, workspace_id, user.id)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member"
        )
    member = add_workspace_member(session, workspace_id, user.id, role)
    return WorkspaceMemberOut(
        id=member.id,
        user_id=user.id,
        role=member.role,
        email=user.email,
        full_name=user.full_name,
    )


@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    session: SessionDep,
    workspace_id: UUID,
    user_id: UUID,
    current_user: CurrentUserDep,
) -> None:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    current_role = get_member_role(session, workspace_id, current_user.id)
    if current_role != UserRole.OWNER and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can remove members"
        )
    remove_workspace_member(session, workspace_id, user_id)


@router.patch("/{workspace_id}/members/{user_id}/role", response_model=WorkspaceMemberOut)
def change_member_role(
    session: SessionDep,
    workspace_id: UUID,
    user_id: UUID,
    role: UserRole,
    current_user: CurrentUserDep,
) -> Any:
    workspace = get_workspace(session, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    current_role = get_member_role(session, workspace_id, current_user.id)
    if current_role != UserRole.OWNER and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can change roles"
        )
    member = update_member_role(session, workspace_id, user_id, role)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    from app.crud.user import get_user

    user = get_user(session, user_id)
    return WorkspaceMemberOut(
        id=member.id,
        user_id=user.id,
        role=member.role,
        email=user.email,
        full_name=user.full_name,
    )
