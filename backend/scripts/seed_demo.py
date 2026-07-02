"""Seed demo data into SavvyBoard for screenshots and local testing."""

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlmodel import Session, SQLModel, select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.db import engine
from app.core.security import get_password_hash
from app.models import (
    Board,
    ChangelogEntry,
    Comment,
    FeedbackItem,
    FeedbackStatus,
    User,
    UserRole,
    Vote,
    Workspace,
    WorkspaceMember,
)


def get_or_create_demo_user(session: Session) -> User:
    user = session.exec(select(User).where(User.email == "demo@savvyboard.app")).first()
    if user:
        return user
    user = User(
        id=uuid4(),
        email="demo@savvyboard.app",
        hashed_password=get_password_hash("demo123"),
        full_name="Demo Product Manager",
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(timezone.utc),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_demo_workspace(session: Session, owner: User) -> Workspace:
    workspace = session.exec(select(Workspace).where(Workspace.slug == "savvyboard-demo")).first()
    if workspace:
        return workspace
    workspace = Workspace(
        id=uuid4(),
        name="SavvyBoard Demo",
        slug="savvyboard-demo",
        description="A public demo workspace showing how SavvyBoard helps product teams collect feedback, prioritize a roadmap, and announce releases.",
        is_public=True,
        owner_id=owner.id,
        created_at=datetime.now(timezone.utc),
    )
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    member = WorkspaceMember(
        id=uuid4(),
        workspace_id=workspace.id,
        user_id=owner.id,
        role=UserRole.OWNER,
        created_at=datetime.now(timezone.utc),
    )
    session.add(member)
    session.commit()
    return workspace


def create_boards(session: Session, workspace: Workspace) -> list[Board]:
    board_specs = [
        {
            "name": "Feature Requests",
            "slug": "feature-requests",
            "description": "Suggest and vote on new features.",
            "categories": ["feature", "improvement"],
        },
        {
            "name": "Bug Reports",
            "slug": "bug-reports",
            "description": "Report bugs and track their resolution.",
            "categories": ["bug"],
        },
        {
            "name": "Integrations",
            "slug": "integrations",
            "description": "Ideas for third-party integrations.",
            "categories": ["integration"],
        },
    ]
    boards = []
    for spec in board_specs:
        board = session.exec(
            select(Board).where(Board.workspace_id == workspace.id, Board.slug == spec["slug"])
        ).first()
        if not board:
            board = Board(
                id=uuid4(),
                workspace_id=workspace.id,
                name=spec["name"],
                slug=spec["slug"],
                description=spec["description"],
                category_options=spec["categories"],
                is_public=True,
                created_at=datetime.now(timezone.utc),
            )
            session.add(board)
            session.commit()
            session.refresh(board)
        boards.append(board)
    return boards


def create_feedback(session: Session, boards: list[Board], demo_user: User) -> list[FeedbackItem]:
    items_data = [
        # Feature Requests
        (
            "Dark mode support",
            "A toggle to switch the entire UI to a dark theme.",
            "feature",
            42,
            FeedbackStatus.IN_PROGRESS,
        ),
        (
            "Mobile app",
            "Native iOS and Android apps for managing feedback on the go.",
            "feature",
            38,
            FeedbackStatus.PLANNED,
        ),
        (
            "Slack notifications",
            "Send updates to a Slack channel when feedback status changes.",
            "integration",
            27,
            FeedbackStatus.UNDER_REVIEW,
        ),
        (
            "CSV export",
            "Export feedback and votes to CSV for offline analysis.",
            "feature",
            19,
            FeedbackStatus.UNDER_REVIEW,
        ),
        (
            "SSO with Google",
            "Allow team members to sign in using Google Workspace.",
            "feature",
            15,
            FeedbackStatus.PLANNED,
        ),
        (
            "Webhook events",
            "Expose webhooks for new feedback, votes, and status changes.",
            "integration",
            12,
            FeedbackStatus.UNDER_REVIEW,
        ),
        (
            "Custom branding",
            "Upload a logo and pick brand colors for public pages.",
            "feature",
            9,
            FeedbackStatus.UNDER_REVIEW,
        ),
        (
            "Roadmap embed widget",
            "An embeddable HTML widget for the public roadmap.",
            "feature",
            31,
            FeedbackStatus.SHIPPED,
        ),
        (
            "Comment reactions",
            "Add emoji reactions to comments.",
            "improvement",
            6,
            FeedbackStatus.UNDER_REVIEW,
        ),
        ("Jira sync", "Two-way sync with Jira issues.", "integration", 22, FeedbackStatus.PLANNED),
        # Bug Reports
        (
            "Login redirect loop",
            "Users sometimes get redirected in a loop after login.",
            "bug",
            14,
            FeedbackStatus.IN_PROGRESS,
        ),
        (
            "Vote count cache stale",
            "The vote count on cards doesn't update immediately.",
            "bug",
            8,
            FeedbackStatus.UNDER_REVIEW,
        ),
        (
            "Email notifications not sent",
            "Comment email notifications are not delivered.",
            "bug",
            5,
            FeedbackStatus.PLANNED,
        ),
        (
            "Missing scrollbar on mobile",
            "The public roadmap page doesn't scroll on small screens.",
            "bug",
            11,
            FeedbackStatus.SHIPPED,
        ),
        # Integrations
        (
            "GitHub issue linking",
            "Link feedback items to existing GitHub issues.",
            "integration",
            17,
            FeedbackStatus.UNDER_REVIEW,
        ),
        (
            "Zapier integration",
            "Trigger Zapier workflows from new feedback.",
            "integration",
            13,
            FeedbackStatus.PLANNED,
        ),
    ]

    board_map = {b.slug: b for b in boards}
    created = []
    for title, description, category, votes, status in items_data:
        target_board = board_map["feature-requests"]
        if category == "bug":
            target_board = board_map["bug-reports"]
        elif category == "integration":
            target_board = board_map["integrations"]

        existing = session.exec(
            select(FeedbackItem).where(
                FeedbackItem.board_id == target_board.id, FeedbackItem.title == title
            )
        ).first()
        if existing:
            created.append(existing)
            continue

        item = FeedbackItem(
            id=uuid4(),
            board_id=target_board.id,
            title=title,
            description=description,
            category=category,
            status=status,
            vote_count=votes,
            author_id=demo_user.id,
            author_name=demo_user.full_name,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(item)
        session.commit()
        session.refresh(item)

        for _ in range(votes):
            vote = Vote(
                id=uuid4(),
                feedback_item_id=item.id,
                anonymous_token=f"demo-voter-{uuid4().hex[:8]}",
                created_at=datetime.now(timezone.utc),
            )
            session.add(vote)
        session.commit()
        created.append(item)

    # Add a few comments
    comment_texts = [
        "Would love to see this in the next release!",
        "This is a blocker for our team.",
        "Can we get an ETA on this?",
        "Great idea, adding my vote.",
    ]
    for item in created[:6]:
        for text in comment_texts[:2]:
            comment = Comment(
                id=uuid4(),
                feedback_item_id=item.id,
                author_name="Demo User",
                content=text,
                created_at=datetime.now(timezone.utc),
            )
            session.add(comment)
    session.commit()
    return created


def create_changelog(session: Session, workspace: Workspace, items: list[FeedbackItem]) -> None:
    entries = [
        {
            "title": "Public roadmap embed widget",
            "content": "You can now embed your public roadmap on any website with a simple HTML snippet.\n\nThanks to everyone who voted for this feature!",
            "feedback_item": next((i for i in items if i.title == "Roadmap embed widget"), None),
        },
        {
            "title": "Mobile scrollbar fix",
            "content": "Resolved an issue where the public roadmap page did not scroll correctly on small screens.",
            "feedback_item": next(
                (i for i in items if i.title == "Missing scrollbar on mobile"), None
            ),
        },
        {
            "title": "New feedback boards",
            "content": "We added dedicated boards for feature requests, bug reports, and integrations to keep feedback organized.",
            "feedback_item": None,
        },
    ]

    for entry in entries:
        existing = session.exec(
            select(ChangelogEntry).where(
                ChangelogEntry.workspace_id == workspace.id, ChangelogEntry.title == entry["title"]
            )
        ).first()
        if existing:
            continue
        changelog = ChangelogEntry(
            id=uuid4(),
            workspace_id=workspace.id,
            title=entry["title"],
            content=entry["content"],
            shipped_at=datetime.now(timezone.utc),
            feedback_item_id=entry["feedback_item"].id if entry["feedback_item"] else None,
            created_at=datetime.now(timezone.utc),
        )
        session.add(changelog)
    session.commit()


def seed() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = get_or_create_demo_user(session)
        workspace = create_demo_workspace(session, user)
        boards = create_boards(session, workspace)
        items = create_feedback(session, boards, user)
        create_changelog(session, workspace, items)
        print(f"Seeded demo workspace: /w/{workspace.slug}")
        print(f"Demo login: {user.email} / demo123")


if __name__ == "__main__":
    seed()
