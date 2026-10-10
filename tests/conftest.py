import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import api, storage
from src.database import Base, get_session


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    sessions = sessionmaker(engine)

    def session_override():
        with sessions() as session:
            yield session

    monkeypatch.setattr(api, "init_db", lambda: None)
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path / "uploads")
    api.app.dependency_overrides[get_session] = session_override
    with TestClient(api.app) as test_client:
        yield test_client
    api.app.dependency_overrides.clear()
    engine.dispose()
