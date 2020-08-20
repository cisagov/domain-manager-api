"""A sample python script."""
# Standard Python Libraries
import os

# Third-Party Libraries
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()
URL = os.environ.get("API_URL")
API_KEY = os.environ.get("API_KEY")

# Pass in api key for authorized access
auth = {"api_key": API_KEY}


def get_domain_list():
    """Returns a list of available domains from Route53."""
    resp = requests.get(f"{URL}/api/domains/", headers=auth)
    return resp.json()


def get_website_content_list():
    """Returns a list of available website content from S3."""
    resp = requests.get(f"{URL}/api/websites/", headers=auth)
    return resp.json()


def get_application_list():
    """Returns a list of applications."""
    resp = requests.get(f"{URL}/api/websites/", headers=auth)
    return resp.json()


def get_live_website_list():
    """Returns a list of active websites."""
    resp = requests.get(f"{URL}/api/live-sites/", headers=auth)
    return resp.json()


def launch_live_website(application_id, domain_id, website_id):
    """
    Launch a live website.

    Input data accessed by id:
    Application that will be using active site.
    A Registered Domain.
    Website content URL.
    """
    post_data = {
        "application_id": application_id,
        "domain_id": domain_id,
        "website_id": website_id,
    }
    resp = requests.post(f"{URL}/api/live-sites/", headers=auth, data=post_data)
    return resp.json()


def categorize_live_site(live_site_id):
    """
    Categorize an active site.

    Check if the domain has already been categorized.
    Categorize the domain on multiple proxies.
    """
    resp = requests.get(f"{URL}/api/categorize/{live_site_id}/", headers=auth)
    return resp.json()


if __name__ == "__main__":
    domain_list = get_domain_list()
    content_list = get_website_content_list()
    application_list = get_application_list()
