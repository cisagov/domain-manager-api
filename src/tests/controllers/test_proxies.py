"""Proxies controller tests."""
# Standard Python Libraries
from datetime import datetime
import json
from unittest import mock

# Third-Party Libraries
from bson.objectid import ObjectId
from faker import Faker
import pytest

# cisagov Libraries
from api.controllers.proxies import proxy_manager
from models.proxy import Proxy

faker = Faker()


@mock.patch.object(Proxy, "create")
def test_post_proxy(mock_create, app):
    """Test creating a proxy."""
    name = faker.company()
    url = faker.url()

    request_context = app.test_request_context(
        "/proxies/",
        method="POST",
        json={"name": name, "url": url, "script": "driver.find_element()"},
    )

    mock_create.attribute = "inserted_id"
    mock_create.inserted_id = "proxy_id"

    response = proxy_manager(request_context.request)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_create.call_args_list)


@mock.patch.object(Proxy, "all")
def test_get_proxies(mock_get_all, app):
    """Test get proxy list."""
    mock_get_all.return_value = [
        {
            "_id": ObjectId("5f36fa1379afa7e91d227d8d"),
            "name": "Trusted Source",
            "url": "url",
            "script": "script",
            "created_by": "dev_user",
            "created_date": datetime(2020, 8, 14, 20, 54, 43, 58000),
        },
        {
            "_id": ObjectId("5f381a6828aa79b2bf8ab84b"),
            "name": "Fortiguard",
            "url": "url",
            "script": "script",
            "created_by": "dev_user",
            "created_date": datetime(2020, 8, 15, 17, 24, 56, 100000),
        },
        {
            "_id": ObjectId("5f3c9b58d99d0cb8ce2e45f7"),
            "name": "Blue Coat",
            "url": "url",
            "script": "script",
            "created_by": "dev_user",
            "created_date": datetime(2020, 8, 19, 3, 24, 8, 411000),
        },
    ]

    request_context = app.test_request_context("/proxies/", method="GET")

    response = proxy_manager(request_context.request)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get_all.call_args_list)


@mock.patch.object(Proxy, "get")
def test_get_proxy(mock_get, app):
    """Test get a proxy."""
    name = faker.company()
    proxy_id = faker.pyint()

    mock_get.return_value = {
        "_id": ObjectId("5f36fa1379afa7e91d227d8d"),
        "name": name,
        "requester_name": "dev_user",
        "requested_date": datetime(2020, 8, 14, 20, 54, 43, 58000),
    }

    request_context = app.test_request_context(f"/proxy/{proxy_id}/", method="GET")

    response = proxy_manager(request_context.request, proxy_id=proxy_id)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get.call_args_list)


@mock.patch.object(Proxy, "update")
def test_update_proxy(mock_update, app):
    """Test update a proxy."""
    name = faker.company()
    proxy_id = faker.pyint()

    mock_update.return_value = {
        "_id": ObjectId("5f36fa1379afa7e91d227d8d"),
        "name": name,
        "requester_name": "dev_user",
        "requested_date": datetime(2020, 8, 14, 20, 54, 43, 58000),
    }

    request_context = app.test_request_context(
        "/proxy/proxy-id/", method="PUT", json={"name": name}
    )

    response = proxy_manager(request_context.request, proxy_id=proxy_id)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_update.call_args_list)


@mock.patch.object(Proxy, "delete")
def test_delete_proxy(mock_delete, app):
    """Test delete an proxy."""
    proxy_id = faker.pyint()

    request_context = app.test_request_context("/proxy/proxy-id/", method="DELETE")

    response = proxy_manager(request_context.request, proxy_id=proxy_id)

    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_delete.call_args_list)
