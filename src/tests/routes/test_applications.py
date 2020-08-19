"""Application endpoint tests."""
# Standard Python Libraries
import json
from unittest import mock

# Third-Party Libraries
from api.documents.application_documents import Application
from faker import Faker
import pytest

faker = Faker()


@mock.patch.object(Application, "create")
def test_post_application(mock_create, client, auth_header):
    """Test creating an application endpoint."""
    response = client.post(
        "/api/applications/",
        headers=auth_header,
        data=json.dumps(dict(name=faker.company())),
        content_type="application/json",
    )

    assert response.status_code == 200
    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_create.call_args_list)


@mock.patch.object(Application, "get_all")
def test_get_applications(mock_get_all, client, auth_header):
    """Test get application list endpoint."""
    response = client.get("/api/applications/", headers=auth_header)

    assert response.status_code == 200
    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get_all.call_args_list)
