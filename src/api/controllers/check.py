"""Check categories controller."""
from utils.categorization.modules import (
    trustedsource,
    bluecoat,
    ciscotalos,
    ibmxforce,
    fortiguard,
)


def check_categories_manager(domain):
    """Check domain categorization manager."""
    return {
        "Trusted Source": trustedsource.check_category(domain),
        "Bluecoat": bluecoat.check_category(domain),
        "Cisco Talos": ciscotalos.check_category(domain),
        "IBM X-Force": ibmxforce.check_category(domain),
        "Fortiguard": fortiguard.check_category(domain),
    }
