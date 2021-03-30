"""Application View Tests."""
# Standard Python Libraries
import json

# cisagov Libraries
from tests.data.application_data import get_applications


def test_applications_get(client, mocker):
    """Test getting list of applications."""
    mocker.patch("api.manager.ApplicationManager.all", return_value=get_applications(5))
    resp = client.get("/api/applications/")
    data = json.loads(resp.data)
    assert len(data) == 5
