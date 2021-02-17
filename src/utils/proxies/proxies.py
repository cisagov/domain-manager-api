"""Proxy helpers."""
# cisagov Libraries
from utils.proxies import (
    bluecoat,
    fortiguard,
    palo_alto,
    trendmicro,
    trusted_source,
    websense,
)


def get_check_proxies():
    """Get proxies to check category with."""
    return {
        "Blue Coat": bluecoat.check_category,
        # "Cisco Talos": ciscotalos.check_category,
        "Fortiguard": fortiguard.check_category,
        # "IBM X Force": ibmxforce.check_category,
        "Trend Micro": trendmicro.check_category,
        "Trusted Source": trusted_source.check_category,
        "Websense": websense.check_category,
    }


def get_check_proxy_func(proxy_name):
    """Get function to check category from proxy name."""
    return get_check_proxies().get(proxy_name)


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
