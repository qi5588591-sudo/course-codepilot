import pytest
from fastapi.testclient import TestClient

from backend.config import Settings
from backend.main import create_app


@pytest.fixture
def settings(tmp_path):
    return Settings(_env_file=None, database=str(tmp_path / "history.sqlite3"))


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        yield client
