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


def get_live_site_list():
    """Returns a list of active websites."""
    resp = requests.get(f"{URL}/api/live-sites/", headers=auth, verify=False)
    return resp.json()


if __name__ == "__main__":
    # Pull available data from the database
    print(
        """
    **** Domains ****
    """
    )
    [print(domain.get("Name")) for domain in get_domain_list()]
    print(
        """
    **** Website Content ****
    """
    )
    [print(content.get("name")) for content in get_website_content_list()]
    print(
        """
    **** Applications ****
    """
    )
    [print(application.get("name")) for application in get_application_list()]
    print(
        """
    **** Live Sites ****
    """
    )
    [print(site.get("name")) for site in get_live_site_list()]
