"""Unit testing config."""
# Standard Python Libraries
import os

# Third-Party Libraries
import pytest

# cisagov Libraries
from main import app as current_app

API_KEY = os.environ.get("API_KEY")


@pytest.fixture
def auth_header():
    """Get api key for authorized access."""
    return {"api_key": API_KEY}


@pytest.fixture
def app():
    """App fixture."""
    yield current_app


@pytest.fixture
def client(app):
    """Initialize test client."""
    app.config["TESTING"] = True

    return app.test_client()
