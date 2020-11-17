"""Application controller tests."""
# Standard Python Libraries
from datetime import datetime
import json
from unittest import mock

# Third-Party Libraries
from api.controllers.applications import applications_manager
from models.application import Application
from bson.objectid import ObjectId
from faker import Faker
import pytest


faker = Faker()


@mock.patch.object(Application, "create")
def test_post_application(mock_create, app):
    """Test creating an application."""
    name = faker.company()

    request_context = app.test_request_context(
        "/applications/", method="POST", json={"name": name}
    )

    mock_create.attribute = "inserted_id"
    mock_create.inserted_id = "application-id"

    response = applications_manager(request_context.request)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_create.call_args_list)


@mock.patch.object(Application, "all")
def test_get_applications(mock_get_all, app):
    """Test get application list."""
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

    request_context = app.test_request_context("/applications/", method="GET")

    response = applications_manager(request_context.request)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get_all.call_args_list)


@mock.patch.object(Application, "get")
def test_get_application(mock_get, app):
    """Test get an application."""
    name = faker.company()
    application_id = faker.pyint()

    mock_get.return_value = {
        "_id": ObjectId("5f36fa1379afa7e91d227d8d"),
        "name": name,
        "requester_name": "dev_user",
        "requested_date": datetime(2020, 8, 14, 20, 54, 43, 58000),
    }

    request_context = app.test_request_context(
        f"/application/{application_id}/", method="GET"
    )

    response = applications_manager(
        request_context.request, application_id=application_id
    )

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get.call_args_list)


@mock.patch.object(Application, "update")
def test_update_application(mock_update, app):
    """Test update an application."""
    name = faker.company()
    application_id = faker.pyint()

    mock_update.return_value = {
        "_id": ObjectId("5f36fa1379afa7e91d227d8d"),
        "name": name,
        "requester_name": "dev_user",
        "requested_date": datetime(2020, 8, 14, 20, 54, 43, 58000),
    }

    request_context = app.test_request_context(
        "/application/application-id/", method="PUT", json={"name": name}
    )

    response = applications_manager(
        request_context.request, application_id=application_id
    )

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_update.call_args_list)


@mock.patch.object(Application, "delete")
def test_delete_application(mock_delete, app):
    """Test delete an application."""
    application_id = faker.pyint()

    request_context = app.test_request_context(
        "/application/application-id/", method="DELETE"
    )

    response = applications_manager(
        request_context.request, application_id=application_id
    )

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_delete.call_args_list)
