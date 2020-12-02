"""Static site utilities."""
# Third-Party Libraries
import requests
from settings import STATIC_GEN_URL


def generate_site(category, domain):
    """Generate a static site."""
    resp = requests.get(
        f"{STATIC_GEN_URL}/website/?category={category}&domain={domain}"
    )
    return {"message": resp.status_code}


def delete_site(category, domain):
    """Delete a static site."""
    resp = requests.delete(
        f"{STATIC_GEN_URL}/website/?category={category}&domain={domain}"
    )

    return {"message": resp.status_code}
