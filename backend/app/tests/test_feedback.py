"""Tests for feedback listing with search, filter, and sort query parameters."""

from datetime import UTC, datetime
from uuid import uuid4

from app.crud.board import create_board
from app.crud.feedback import (
    FeedbackSort,
    create_feedback_item,
    list_feedback_items,
)
from app.crud.user import create_user
from app.models import FeedbackStatus
from app.schemas.board import BoardCreate
from app.schemas.feedback import FeedbackItemCreate
from app.schemas.user import UserCreate


def _seed_board_and_items(session):
    """Create a workspace, board, and several feedback items for testing."""
    from app.crud.workspace import create_workspace
    from app.schemas.workspace import WorkspaceCreate

    user = create_user(
        session,
        UserCreate(email="owner@example.com", password="testpass123", full_name="Owner"),
    )
    workspace = create_workspace(
        session,
        WorkspaceCreate(name="Test WS", slug="test-ws", is_public=True),
        owner_id=user.id,
    )
    board = create_board(
        session,
        workspace.id,
        BoardCreate(name="General", slug="general", is_public=True),
    )

    # Items with varied categories, statuses, vote counts, and created_at offsets.
    base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    items_data = [
        {
            "title": "Dark mode for dashboard",
            "description": "Please add a dark theme.",
            "category": "feature",
            "status": FeedbackStatus.UNDER_REVIEW,
            "votes": 5,
            "created_offset": 0,
        },
        {
            "title": "Login page crash on Safari",
            "description": "The login form crashes on Safari 17.",
            "category": "bug",
            "status": FeedbackStatus.IN_PROGRESS,
            "votes": 10,
            "created_offset": 1,
        },
        {
            "title": "Improve loading speed",
            "description": "Pages take too long to load.",
            "category": "improvement",
            "status": FeedbackStatus.PLANNED,
            "votes": 3,
            "created_offset": 2,
        },
        {
            "title": "Slack integration",
            "description": "Send notifications to Slack.",
            "category": "integration",
            "status": FeedbackStatus.SHIPPED,
            "votes": 20,
            "created_offset": 3,
        },
        {
            "title": "Export to CSV",
            "description": "Allow exporting feedback data to CSV for dark mode analysis.",
            "category": "feature",
            "status": FeedbackStatus.UNDER_REVIEW,
            "votes": 1,
            "created_offset": 4,
        },
    ]

    items = []
    for data in items_data:
        item = create_feedback_item(
            session,
            board.id,
            FeedbackItemCreate(
                title=data["title"],
                description=data["description"],
                category=data["category"],
            ),
            user_id=user.id,
        )
        # Manually set status, simulate votes, and set distinct timestamps for
        # deterministic sort testing (SQLite may truncate sub-second precision).
        item.status = data["status"]
        item.vote_count = data["votes"]
        item.created_at = base_time.replace(minute=data["created_offset"])
        item.updated_at = base_time.replace(minute=data["created_offset"])
        session.add(item)
        session.commit()
        session.refresh(item)
        items.append(item)

    return workspace, board, items


def test_list_feedback_default_sorts_by_top_voted(session):
    _, board, items = _seed_board_and_items(session)

    result = list_feedback_items(session, board.id)
    assert [r.id for r in result] == [
        items[3].id,  # 20 votes
        items[1].id,  # 10 votes
        items[0].id,  # 5 votes
        items[2].id,  # 3 votes
        items[4].id,  # 1 vote
    ]


def test_list_feedback_sort_newest(session):
    _, board, items = _seed_board_and_items(session)

    result = list_feedback_items(session, board.id, sort=FeedbackSort.NEWEST)
    # Items are created in order, so newest is the last created.
    assert result[0].id == items[4].id
    assert result[-1].id == items[0].id


def test_list_feedback_sort_oldest(session):
    _, board, items = _seed_board_and_items(session)

    result = list_feedback_items(session, board.id, sort=FeedbackSort.OLDEST)
    assert result[0].id == items[0].id
    assert result[-1].id == items[4].id


def test_list_feedback_search_by_title(session):
    _, board, items = _seed_board_and_items(session)

    result = list_feedback_items(session, board.id, search="dark mode")
    titles = [r.title for r in result]
    assert "Dark mode for dashboard" in titles
    assert "Export to CSV" in titles  # description mentions "dark mode"
    assert "Login page crash on Safari" not in titles


def test_list_feedback_search_case_insensitive(session):
    _, board, _ = _seed_board_and_items(session)

    result = list_feedback_items(session, board.id, search="SLACK")
    assert len(result) == 1
    assert result[0].title == "Slack integration"


def test_list_feedback_search_no_matches(session):
    _, board, _ = _seed_board_and_items(session)

    result = list_feedback_items(session, board.id, search="nonexistent-feature-name")
    assert result == []


def test_list_feedback_filter_by_category(session):
    _, board, _ = _seed_board_and_items(session)

    result = list_feedback_items(session, board.id, category="bug")
    assert len(result) == 1
    assert result[0].category == "bug"


def test_list_feedback_filter_by_status(session):
    _, board, _ = _seed_board_and_items(session)

    result = list_feedback_items(session, board.id, status=FeedbackStatus.UNDER_REVIEW)
    assert len(result) == 2
    assert all(r.status == FeedbackStatus.UNDER_REVIEW for r in result)


def test_list_feedback_combined_search_and_category(session):
    _, board, _ = _seed_board_and_items(session)

    result = list_feedback_items(
        session, board.id, search="CSV", category="feature"
    )
    assert len(result) == 1
    assert result[0].title == "Export to CSV"


def test_list_feedback_combined_filter_and_sort(session):
    _, board, _ = _seed_board_and_items(session)

    result = list_feedback_items(
        session, board.id, category="feature", sort=FeedbackSort.NEWEST
    )
    assert len(result) == 2
    assert all(r.category == "feature" for r in result)
    # Newest first: "Export to CSV" was created after "Dark mode for dashboard".
    assert result[0].title == "Export to CSV"


def test_list_feedback_invalid_board_returns_empty(session):
    result = list_feedback_items(session, uuid4())
    assert result == []


# --- API-level tests via TestClient ---


def _register_and_login(client):
    """Register a user and return auth headers + user id."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "feedbackuser@example.com",
            "password": "testpass123",
            "full_name": "Feedback User",
        },
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "feedbackuser@example.com", "password": "testpass123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_workspace_board_and_items(client, session):
    """Create a workspace, board, and items via CRUD and return IDs."""
    from app.crud.board import create_board
    from app.crud.feedback import create_feedback_item
    from app.crud.workspace import create_workspace
    from app.crud.user import get_user_by_email
    from app.schemas.board import BoardCreate
    from app.schemas.feedback import FeedbackItemCreate
    from app.schemas.workspace import WorkspaceCreate

    user = get_user_by_email(session, "feedbackuser@example.com")
    workspace = create_workspace(
        session,
        WorkspaceCreate(name="FB WS", slug="fb-ws", is_public=True),
        owner_id=user.id,
    )
    board = create_board(
        session,
        workspace.id,
        BoardCreate(name="General", slug="general", is_public=True),
    )

    item1 = create_feedback_item(
        session,
        board.id,
        FeedbackItemCreate(title="Feature A", description="desc A", category="feature"),
        user_id=user.id,
    )
    item1.status = FeedbackStatus.UNDER_REVIEW
    item1.vote_count = 5
    item1.created_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    item1.updated_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    session.add(item1)

    item2 = create_feedback_item(
        session,
        board.id,
        FeedbackItemCreate(title="Bug Report B", description="desc B", category="bug"),
        user_id=user.id,
    )
    item2.status = FeedbackStatus.IN_PROGRESS
    item2.vote_count = 15
    item2.created_at = datetime(2026, 1, 1, 12, 1, 0, tzinfo=UTC)
    item2.updated_at = datetime(2026, 1, 1, 12, 1, 0, tzinfo=UTC)
    session.add(item2)

    session.commit()

    return workspace, board


def test_api_list_feedback_with_search(client, session):
    headers = _register_and_login(client)
    workspace, board = _create_workspace_board_and_items(client, session)

    resp = client.get(
        f"/api/v1/workspaces/{workspace.id}/boards/{board.id}/feedback/",
        params={"search": "Feature"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Feature A"


def test_api_list_feedback_with_category_filter(client, session):
    headers = _register_and_login(client)
    workspace, board = _create_workspace_board_and_items(client, session)

    resp = client.get(
        f"/api/v1/workspaces/{workspace.id}/boards/{board.id}/feedback/",
        params={"category": "bug"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["category"] == "bug"


def test_api_list_feedback_with_sort_newest(client, session):
    headers = _register_and_login(client)
    workspace, board = _create_workspace_board_and_items(client, session)

    resp = client.get(
        f"/api/v1/workspaces/{workspace.id}/boards/{board.id}/feedback/",
        params={"sort": "newest"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["title"] == "Bug Report B"  # created second -> newest


def test_api_list_feedback_with_sort_top_voted(client, session):
    headers = _register_and_login(client)
    workspace, board = _create_workspace_board_and_items(client, session)

    resp = client.get(
        f"/api/v1/workspaces/{workspace.id}/boards/{board.id}/feedback/",
        params={"sort": "top_voted"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["title"] == "Bug Report B"  # 15 votes > 5 votes


def test_api_list_feedback_with_status_filter(client, session):
    headers = _register_and_login(client)
    workspace, board = _create_workspace_board_and_items(client, session)

    resp = client.get(
        f"/api/v1/workspaces/{workspace.id}/boards/{board.id}/feedback/",
        params={"status": "in_progress"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "in_progress"


def test_api_list_feedback_invalid_sort_value(client, session):
    headers = _register_and_login(client)
    workspace, board = _create_workspace_board_and_items(client, session)

    resp = client.get(
        f"/api/v1/workspaces/{workspace.id}/boards/{board.id}/feedback/",
        params={"sort": "invalid_sort"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_public_list_feedback_with_search(client, session):
    _register_and_login(client)
    workspace, board = _create_workspace_board_and_items(client, session)

    resp = client.get(
        f"/api/v1/public/workspaces/fb-ws/feedback/general",
        params={"search": "Bug"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Bug Report B"


def test_public_list_feedback_with_category_and_sort(client, session):
    _register_and_login(client)
    workspace, board = _create_workspace_board_and_items(client, session)

    resp = client.get(
        f"/api/v1/public/workspaces/fb-ws/feedback/general",
        params={"category": "feature", "sort": "newest"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["category"] == "feature"


def test_public_list_feedback_without_filters_returns_all(client, session):
    _register_and_login(client)
    workspace, board = _create_workspace_board_and_items(client, session)

    resp = client.get(f"/api/v1/public/workspaces/fb-ws/feedback/general")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2