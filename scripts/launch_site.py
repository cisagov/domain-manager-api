"""A sample python script."""
# Standard Python Libraries
import os

# Third-Party Libraries
from dotenv import load_dotenv
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


# Disable insecure request warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()
URL = os.environ.get("API_URL")
API_KEY = os.environ.get("API_KEY")

# Pass in api key for authorized access
auth = {"api_key": API_KEY}


def get_domain_list():
    """Returns a list of available domains from Route53."""
    resp = requests.get(f"{URL}/api/domains/", headers=auth, verify=False)
    return resp.json()


def get_website_content_list():
    """Returns a list of available website content from S3."""
    resp = requests.get(f"{URL}/api/websites/", headers=auth, verify=False)
    return resp.json()


def get_application_list():
    """Returns a list of applications."""
    resp = requests.get(f"{URL}/api/applications/", headers=auth, verify=False)
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
    resp = requests.post(
        f"{URL}/api/live-sites/", headers=auth, json=post_data, verify=False
    )

    return resp.json()


if __name__ == "__main__":
    # Pull available data from the database
    domain_list = get_domain_list()
    content_list = get_website_content_list()
    application_list = get_application_list()

    # Define the desired data
    domain_name = input("Please enter domain name: ")
    content_name = input("Please enter content name: ")
    application_name = input("Please enter application name: ")

    # Access data by their uuids
    domain_id = "".join(
        domain.get("_id") for domain in domain_list if domain_name == domain.get("Name")
    )

    content_id = "".join(
        content.get("_id")
        for content in content_list
        if content_name == content.get("name")
    )

    application_id = "".join(
        application.get("_id")
        for application in application_list
        if application_name == application.get("name")
    )

    # Launch website
    active_site = launch_live_website(
        application_id=application_id, domain_id=domain_id, website_id=content_id
    )

    print(active_site)
