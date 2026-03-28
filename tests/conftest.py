import pytest
from app import create_app
from app.extensions import init_mongo

TEST_MONGO_URI = "mongodb://localhost:27017/ms-agent-test"


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["MONGO_URI"] = TEST_MONGO_URI
    init_mongo(flask_app)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_collections():
    yield
    from app.extensions import mongo_db
    if mongo_db is not None:
        mongo_db["conversations"].drop()
        mongo_db["chat_messages"].drop()
