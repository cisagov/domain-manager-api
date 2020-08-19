"""Websites endpoint tests."""
# Standard Python Libraries
import json
from unittest import mock

# Third-Party Libraries
from api.documents.website_documents import Website
from faker import Faker
import pytest

faker = Faker()


@mock.patch.object(Website, "get_all")
def test_get_websites(mock_get_all, client, auth_header):
    """Test get website content list endpoint."""
    response = client.get("/api/websites/", headers=auth_header)

    assert response.status_code == 200
    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get_all.call_args_list)
