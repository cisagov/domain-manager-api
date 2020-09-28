"""Check categories controller."""
from utils.categorization import (
    trustedsource,
    bluecoat,
    ciscotalos,
    ibmxforce,
    fortiguard,
    websense,
)


def check_categories_manager(domain):
    """Check domain categorization manager."""
    return {
        "Trusted Source": trustedsource.check_category(domain),
        "Bluecoat": bluecoat.check_category(domain),
        "Cisco Talos": ciscotalos.check_category(domain),
        "IBM X-Force": ibmxforce.check_category(domain),
        "Fortiguard": fortiguard.check_category(domain),
        "Websense": websense.check_category(domain),
    }
