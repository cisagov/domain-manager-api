"""Static site utilities."""
# Third-Party Libraries
import requests
from settings import STATIC_GEN_URL


def generate_site():
    """Generate a static site."""
    resp = requests.get(f"{STATIC_GEN_URL}/website/")
    return {"message": resp.status_code}
