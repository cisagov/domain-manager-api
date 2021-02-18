"""IBM X-Force categorization check."""
# Standard Python Libraries
import os

# Third-Party Libraries
import requests
from requests.auth import HTTPBasicAuth

IBM_API_KEY = os.environ.get("IBM_API_KEY")
IBM_API_PASS = os.environ.get("IBM_API_PASS")


def check_category(domain):
    """Check domain category on IBM X-Force."""
    print("Checking IBM X-Force proxy")
    headers = {"Accept": "application/json"}
    resp = requests.get(
        f"https://api.xforce.ibmcloud.com/url/{domain}",
        headers=headers,
        auth=HTTPBasicAuth(
            IBM_API_KEY,
            IBM_API_PASS,
        ),
    )

    return "\n".join(resp.json()["result"]["cats"].keys())
