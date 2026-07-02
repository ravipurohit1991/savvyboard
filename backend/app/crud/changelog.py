from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, select

from app.models import ChangelogEntry
from app.schemas.changelog import ChangelogEntryCreate, ChangelogEntryUpdate


def get_changelog_entry(session: Session, entry_id: UUID) -> ChangelogEntry | None:
    return session.get(ChangelogEntry, entry_id)


def list_changelog_entries(session: Session, workspace_id: UUID) -> list[ChangelogEntry]:
    statement = (
        select(ChangelogEntry)
        .where(ChangelogEntry.workspace_id == workspace_id)
        .order_by(ChangelogEntry.shipped_at.desc())
    )
    return list(session.exec(statement).all())


def create_changelog_entry(
    session: Session, workspace_id: UUID, entry_in: ChangelogEntryCreate
) -> ChangelogEntry:
    entry = ChangelogEntry(
        workspace_id=workspace_id,
        title=entry_in.title,
        content=entry_in.content,
        shipped_at=entry_in.shipped_at or datetime.now(UTC),
        feedback_item_id=entry_in.feedback_item_id,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def update_changelog_entry(
    session: Session, entry: ChangelogEntry, entry_in: ChangelogEntryUpdate
) -> ChangelogEntry:
    update_data = entry_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def delete_changelog_entry(session: Session, entry: ChangelogEntry) -> None:
    session.delete(entry)
    session.commit()
