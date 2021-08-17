"""Categorization utils."""
# cisagov Libraries
from api.manager import DomainManager
from utils.categorization import CATEGORIES, PROXIES

domain_manager = DomainManager()


def categorize(requested_category, domain_name):
    """Categorize a domain across proxies."""
    return CATEGORIES


def verify(domain_name, category_name):
    """Verify domain has been categorized."""
    return PROXIES
