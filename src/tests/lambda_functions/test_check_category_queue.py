"""Tests for check category lambda."""
# Third-Party Libraries
from lambda_functions.check_category_queue import handler
from moto import mock_sqs

# cisagov Libraries
from tests.data.domain_data import get_domains


@mock_sqs
def test_handler(mocker):
    """Test check category queue."""
    mock_domain = mocker.patch(
        "api.manager.DomainManager.all", return_value=get_domains(3)
    )
    handler(None, None)

    assert mock_domain.called
