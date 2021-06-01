"""Site handler function tests."""
# Third-Party Libraries
import pytest

# cisagov Libraries
from utils.aws import site_handler


def test_verify_launch_records():
    """Test verify launch records."""
    domain = {"name": "test.xyz"}
    with pytest.raises(Exception):
        domain["records"] = [{"name": "test.xyz", "record_type": "A"}]
        site_handler.verify_launch_records(domain)

    with pytest.raises(Exception):
        domain["records"] = [{"name": "www.test.xyz", "record_type": "A"}]
        site_handler.verify_launch_records(domain)

    domain["records"] = []
    site_handler.verify_launch_records(domain)

    domain["records"] = [{"name": "test.test.xyz", "record_type": "A"}]
    site_handler.verify_launch_records(domain)
