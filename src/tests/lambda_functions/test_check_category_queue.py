"""Tests for check category lambda."""
# cisagov Libraries
from lambda_functions.check_category_queue import handler
from tests.data.domain_data import get_domains


def test_handler(mocker):
    """Test check category queue."""
    mock_domain = mocker.patch(
        "api.manager.DomainManager.all", return_value=get_domains(3)
    )
    mocker.patch("boto3.client")
    # mock_send_message = mocker.patch("boto3.client.send_message")
    handler(None, None)

    assert mock_domain.called
    # assert mock_send_message.called
