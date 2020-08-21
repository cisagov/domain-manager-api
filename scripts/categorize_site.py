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


def get_live_site_list():
    """Returns a list of active websites."""
    resp = requests.get(f"{URL}/api/live-sites/", headers=auth, verify=False)
    return resp.json()


def categorize_live_site(live_site_id):
    """
    Categorize an active site.

    Check if the domain has already been categorized.
    Categorize the domain on multiple proxies.
    """
    resp = requests.get(
        f"{URL}/api/categorize/{live_site_id}/", headers=auth, verify=False
    )

    return resp.json()


if __name__ == "__main__":
    # Pull available live sites
    live_sites = get_live_site_list()

    # Define the desired site name from list
    site_name = input("Please enter site name: ")

    # Access live site data by uuid
    live_site_id = "".join(
        site.get("_id") for site in live_sites if site_name == site.get("name")
    )

    # Categorize site
    categorized = categorize_live_site(live_site_id=live_site_id)

    print(categorized)
