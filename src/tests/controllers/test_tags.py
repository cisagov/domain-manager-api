"""Tag controller tests."""
# Standard Python Libraries
from datetime import datetime
import json
from unittest import mock

# Third-Party Libraries
from api.controllers.tags import tags_manager
from api.documents.tag import Tag
from bson.objectid import ObjectId
from faker import Faker
import pytest

faker = Faker()


@mock.patch.object(Tag, "create")
def test_post_tag(mock_create, app):
    """Test creating an tag."""
    name = faker.company()

    request_context = app.test_request_context(
        "/tags/", method="POST", json={"name": name}
    )

    mock_create.attribute = "inserted_id"
    mock_create.inserted_id = "tag-id"

    response = tags_manager(request_context.request)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_create.call_args_list)


@mock.patch.object(Tag, "get_all")
def test_get_tags(mock_get_all, app):
    """Test get tag list."""
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

    request_context = app.test_request_context("/tags/", method="GET")

    response = tags_manager(request_context.request)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get_all.call_args_list)


@mock.patch.object(Tag, "get_by_id")
def test_get_tag(mock_get, app):
    """Test get an tag."""
    name = faker.company()
    tag_id = faker.pyint()

    mock_get.return_value = {
        "_id": ObjectId("5f36fa1379afa7e91d227d8d"),
        "name": name,
        "requester_name": "dev_user",
        "requested_date": datetime(2020, 8, 14, 20, 54, 43, 58000),
    }

    request_context = app.test_request_context(f"/tag/{tag_id}/", method="GET")

    response = tags_manager(request_context.request, tag_id=tag_id)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get.call_args_list)


@mock.patch.object(Tag, "update")
def test_update_tag(mock_update, app):
    """Test update an tag."""
    name = faker.company()
    tag_id = faker.pyint()

    mock_update.return_value = {
        "_id": ObjectId("5f36fa1379afa7e91d227d8d"),
        "name": name,
        "requester_name": "dev_user",
        "requested_date": datetime(2020, 8, 14, 20, 54, 43, 58000),
    }

    request_context = app.test_request_context(
        "/tag/tag-id/", method="PUT", json={"name": name}
    )

    response = tags_manager(request_context.request, tag_id=tag_id)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_update.call_args_list)


@mock.patch.object(Tag, "delete")
def test_delete_tag(mock_delete, app):
    """Test delete an tag."""
    tag_id = faker.pyint()

    request_context = app.test_request_context("/tag/tag-id/", method="DELETE")

    response = tags_manager(request_context.request, tag_id=tag_id)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_delete.call_args_list)
