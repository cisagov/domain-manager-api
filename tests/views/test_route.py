"""Application View Tests."""


class SampleResponse:
    """SampleResponse for requests."""

    text = "test"


def test_route_get(client, mocker):
    """Test getting list of applications."""
    mocker.patch("requests.get", return_value=SampleResponse())
    resp = client.get("/")
    assert resp.status_code == 200
