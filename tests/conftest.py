import pytest
from unittest.mock import MagicMock
from app import create_app
import app.extensions as extensions


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(extensions, "mongo_db", MagicMock())
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()
