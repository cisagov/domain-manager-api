"""Application View Tests."""


def test_route_get(client, mocker):
    """Test getting list of applications."""
    resp = client.get("/")
    assert resp.status_code == 200
