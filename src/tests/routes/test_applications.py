"""Application endpoint tests."""
# Standard Python Libraries
from datetime import datetime
import json
from unittest import mock

# Third-Party Libraries
from api.documents.application import Application
from bson.objectid import ObjectId
from faker import Faker
import pytest

faker = Faker()


@mock.patch.object(Application, "create")
def test_post_application(mock_create, client, auth_header):
    """Test creating an application endpoint."""
    name = faker.company()

    response = client.post(
        "/api/applications/",
        headers=auth_header,
        data=json.dumps(dict(name=name)),
        content_type="application/json",
    )

    assert response.status_code == 200
    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_create.call_args_list)


@mock.patch.object(Application, "get_all")
def test_get_applications(mock_get_all, client, auth_header):
    """Test get application list endpoint."""
    mock_get_all.return_value = [
        {
            "_id": ObjectId("5f36fa1379afa7e91d227d8d"),
            "name": "DHS Red Team",
            "requester_name": "dev_user",
            "requested_date": datetime(2020, 8, 14, 20, 54, 43, 58000),
        },
        {
            "_id": ObjectId("5f381a6828aa79b2bf8ab84b"),
            "name": "Con-PCA",
            "requester_name": "dev_user",
            "requested_date": datetime(2020, 8, 15, 17, 24, 56, 100000),
        },
        {
            "_id": ObjectId("5f3c9b58d99d0cb8ce2e45f7"),
            "name": "DHS Blue Team",
            "requester_name": "dev_user",
            "requested_date": datetime(2020, 8, 19, 3, 24, 8, 411000),
        },
    ]

    response = client.get("/api/applications/", headers=auth_header)

    assert response.status_code == 200
    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get_all.call_args_list)
