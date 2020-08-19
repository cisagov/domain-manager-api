"""Swagger endpoint tests."""
# Third-Party Libraries
import pytest


def test_get_docs(client):
    """Test get swagger docs."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"Domain Manager API" in response.data
