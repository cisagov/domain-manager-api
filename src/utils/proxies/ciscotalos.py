"""Cisco Talos categorization check."""
# Standard Python Libraries
import os

# Third-Party Libraries
import requests

CISCO_API_KEY = os.environ.get("CISCO_API_KEY")


def check_category(domain):
    """Check domain category on Cisco Talos."""
    print("Checking Cisco Talos proxy")
    headers = {"Authorization": f"Bearer {CISCO_API_KEY}"}
    resp = requests.get(
        f"https://investigate.api.umbrella.com/domains/categorization/{domain}?showLabels",
        headers=headers,
    )

    return "\n".join(resp.json()[domain]["content_categories"])
