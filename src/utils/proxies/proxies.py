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


def get_check_proxies():
    """Get proxies to check category with."""
    return {
        "bluecoat": bluecoat.check_category,
        "ciscotalos": ciscotalos.check_category,
        "fortiguard": fortiguard.check_category,
        "ibmxforce": ibmxforce.check_category,
        "trusted_source": trusted_source.check_category,
    }


def get_check_proxy_func(proxy_name):
    """Get function to check category from proxy name."""
    return get_check_proxies().get(proxy_name)


def get_categorize_proxies():
    """Get proxies to categorize against."""
    return {
        "bluecoat": bluecoat.categorize,
        "fortiguard": fortiguard.categorize,
        "palo_alto": palo_alto.categorize,
        "trendmicro": trendmicro.categorize,
        "trusted_source": trusted_source.categorize,
    }


def get_categorize_proxy_func(proxy_name):
    """Get function to categorize from proxy name."""
    return get_categorize_proxies().get(proxy_name)
