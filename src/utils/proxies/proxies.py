"""Proxy helpers."""
# cisagov Libraries
from utils.proxies import (
    bluecoat,
    ciscotalos,
    fortiguard,
    ibmxforce,
    palo_alto,
    trendmicro,
    trusted_source,
)


def get_check_proxies(domain):
    """Get proxies to check category with."""
    return {
        "bluecoat": bluecoat.check_category(domain),
        "ciscotalos": ciscotalos.check_category(domain),
        "fortiguard": fortiguard.check_category(domain),
        "ibmxforce": ibmxforce.check_category(domain),
        "trusted_source": trusted_source.check_category(domain),
    }


def get_check_proxy_func(proxy_name, domain):
    """Get function to check category from proxy name."""
    return get_check_proxies(domain).get(proxy_name)


def get_categorize_proxies():
    """Get proxies to categorize against."""
    return {
        "Blue Coat": bluecoat.categorize,
        "Fortiguard": fortiguard.categorize,
        "Palo Alto Networks": palo_alto.categorize,
        "Trend Micro": trendmicro.categorize,
        "Trusted Source": trusted_source.categorize,
    }


def get_categorize_proxy_func(proxy_name):
    """Get function to categorize from proxy name."""
    return get_categorize_proxies().get(proxy_name)
