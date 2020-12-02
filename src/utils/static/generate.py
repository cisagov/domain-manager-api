"""Static site utilities."""
import requests

STATIC_GEN_URL = "http://host.docker.internal:8000"


def generate_site():
    """Generate a static site."""
    resp = requests.post(f"{STATIC_GEN_URL}/website")
    return {"message": resp.status_code}
