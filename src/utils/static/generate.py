"""Static site utilities."""
# Third-Party Libraries
import requests
from settings import STATIC_GEN_URL


def upload_template(category):
    """Upload template files."""
    resp = requests.post(f"{STATIC_GEN_URL}/template/?category={category}")
    return {"message": resp.status_code}


def delete_template(category):
    """Delete template files."""
    resp = requests.delete(f"{STATIC_GEN_URL}/template/?category={category}")
    return {"message": resp.status_code}


def generate_site(category, domain):
    """Generate a static site."""
    post_data = {
        "description": "This is from a POST request",
        "domain": "www.spokanepestservices.com",
        "email": "spokane@mypestcompany.com",
        "name": "My Spokane Pest Services FROM POST",
        "phone": "661-456-7890",
    }
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
