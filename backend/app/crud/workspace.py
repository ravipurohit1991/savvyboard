from uuid import UUID

from sqlmodel import Session, select

from app.models import User, UserRole, Workspace, WorkspaceMember
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


def get_workspace(session: Session, workspace_id: UUID) -> Workspace | None:
    return session.get(Workspace, workspace_id)


def get_workspace_by_slug(session: Session, slug: str) -> Workspace | None:
    statement = select(Workspace).where(Workspace.slug == slug)
    return session.exec(statement).first()


def list_workspaces_for_user(session: Session, user_id: UUID) -> list[Workspace]:
    statement = (
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == user_id)
    )
    return list(session.exec(statement).all())


def create_workspace(
    session: Session, workspace_create: WorkspaceCreate, owner_id: UUID
) -> Workspace:
    workspace = Workspace(
        name=workspace_create.name,
        slug=workspace_create.slug,
        description=workspace_create.description,
        is_public=workspace_create.is_public,
        owner_id=owner_id,
    )
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=owner_id,
        role=UserRole.OWNER,
    )
    session.add(member)
    session.commit()

    return workspace


def update_workspace(
    session: Session, workspace: Workspace, workspace_update: WorkspaceUpdate
) -> Workspace:
    update_data = workspace_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workspace, field, value)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    return workspace


def delete_workspace(session: Session, workspace: Workspace) -> None:
    session.delete(workspace)
    session.commit()


def get_workspace_members(
    session: Session, workspace_id: UUID
) -> list[tuple[WorkspaceMember, User]]:
    statement = (
        select(WorkspaceMember, User)
        .join(User, WorkspaceMember.user_id == User.id)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    return list(session.exec(statement).all())


def add_workspace_member(
    session: Session, workspace_id: UUID, user_id: UUID, role: UserRole
) -> WorkspaceMember:
    member = WorkspaceMember(workspace_id=workspace_id, user_id=user_id, role=role)
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def remove_workspace_member(session: Session, workspace_id: UUID, user_id: UUID) -> None:
    statement = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    )
    member = session.exec(statement).first()
    if member:
        session.delete(member)
        session.commit()


def update_member_role(
    session: Session, workspace_id: UUID, user_id: UUID, role: UserRole
) -> WorkspaceMember | None:
    statement = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    )
    member = session.exec(statement).first()
    if not member:
        return None
    member.role = role
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def get_member_role(session: Session, workspace_id: UUID, user_id: UUID) -> UserRole | None:
    statement = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    )
    member = session.exec(statement).first()
    return member.role if member else None
