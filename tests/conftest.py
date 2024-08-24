from app import create_app, db
from config import TestConfig
from flask_login import FlaskLoginClient
import pytest


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    app.test_client_class = FlaskLoginClient

    with app.app_context():
        db.create_all()

    yield app
