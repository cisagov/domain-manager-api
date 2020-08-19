"""Domains endpoint tests."""
# Standard Python Libraries
import json
from unittest import mock

# Third-Party Libraries
from api.documents.domain import Domain
from faker import Faker
import pytest

faker = Faker()


@mock.patch.object(Domain, "get_all")
def test_get_domains(mock_get_all, client, auth_header):
    """Test get website content list endpoint."""
    response = client.get("/api/domains/", headers=auth_header)

    assert response.status_code == 200
    # Assert mocked method is called with the right parameters
    assert mock.call(response, mock_get_all.call_args_list)
