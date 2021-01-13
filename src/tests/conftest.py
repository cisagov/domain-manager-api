"""Main fixture for testing flask app."""
# Third-Party Libraries
import pytest

# cisagov Libraries
from main import app


@pytest.fixture(scope="session")
def client():
    """Get fixture for client."""
    app.config["TESTING"] = True
    app.config["BCRYPT_LOG_ROUNDS"] = 4
    app.config["WTF_CSRF_ENABLED"] = False
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield testing_client
    ctx.pop()
