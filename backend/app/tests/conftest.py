import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core import db as db_module
from app.main import app


@pytest.fixture(scope="function", autouse=True)
def test_engine(monkeypatch):
    """Replace the global SQLModel engine with a fresh SQLite in-memory engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    SQLModel.metadata.create_all(engine)

    original_engine = db_module.engine
    monkeypatch.setattr(db_module, "engine", engine)

    yield engine

    SQLModel.metadata.drop_all(engine)
    monkeypatch.setattr(db_module, "engine", original_engine)


@pytest.fixture
def session(test_engine):
    with Session(test_engine) as s:
        yield s


@pytest.fixture
def client(test_engine):
    return TestClient(app)
