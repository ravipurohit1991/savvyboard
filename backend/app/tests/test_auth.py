from app.crud.user import authenticate, get_user_by_email
from app.schemas.user import UserCreate


def test_register_and_login(client):
    register_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
        },
    )
    assert register_resp.status_code == 201
    user = register_resp.json()
    assert user["email"] == "test@example.com"
    assert user["full_name"] == "Test User"
    assert "id" in user

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpass123"},
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "test@example.com"


def test_login_with_invalid_credentials(client):
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "wrong"},
    )
    assert resp.status_code == 400


def test_refresh_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "testpass123",
            "full_name": "Refresh User",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@example.com", "password": "testpass123"},
    ).json()

    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login["refresh_token"]},
    )
    assert refresh.status_code == 200
    new_tokens = refresh.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens


def test_authenticate_crud(session):
    from app.crud.user import create_user

    user = create_user(
        session,
        UserCreate(email="crud@example.com", password="hunter2", full_name="CRUD User"),
    )
    assert user.id is not None
    assert get_user_by_email(session, "crud@example.com") is not None

    assert authenticate(session, "crud@example.com", "hunter2") is not None
    assert authenticate(session, "crud@example.com", "wrong") is None
