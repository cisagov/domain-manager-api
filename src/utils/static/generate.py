"""Static site utilities."""
# Third-Party Libraries
import requests
from settings import STATIC_GEN_URL

from models.website import Website


def upload_template(category):
    """Upload template files."""
    resp = requests.post(f"{STATIC_GEN_URL}/template/?category={category}")
    return {"message": resp.status_code}


def delete_template(category):
    """Delete template files."""
    resp = requests.delete(f"{STATIC_GEN_URL}/template/?category={category}")
    return {"message": resp.status_code}


def generate_site(category, website_id):
    """Generate a static site."""
    website = Website(_id=website_id)
    website.get()

    post_data = website.profile
    domain = website.name

    resp = requests.post(
        f"{STATIC_GEN_URL}/website/?category={category}&domain={domain}", json=post_data
    )
    return {"message": resp.status_code}


def delete_site(category, domain):
    """Delete a static site."""
    resp = requests.delete(
        f"{STATIC_GEN_URL}/website/?category={category}&domain={domain}"
    )

    return {"message": resp.status_code}
