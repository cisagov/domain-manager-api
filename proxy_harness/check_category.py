"""Categorization controller. Mac and linux compatible."""
# Standard Python Libraries
import time

# cisagov Libraries
from utils.proxies.proxies import get_check_proxies


def check(domain_name):
    """Categorize site with all proxies in proxies folder."""
    # Submit domain to proxy
    for k, v in get_check_proxies().items():
        try:
            resp = v(domain_name)
            print(f"{k} responsed with {resp}")
            time.sleep(3)
        except Exception as e:
            print(str(e))


domain_name = input("Enter a domain name: ")
check(domain_name)
