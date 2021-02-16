"""Categorization controller. Mac and linux compatible."""
# Standard Python Libraries
import os
import time

# Third-Party Libraries
from selenium import webdriver

# cisagov Libraries
from utils.proxies.proxies import get_check_proxies

# Load environment variables from .env file
script_dir = os.path.dirname(os.path.realpath(__file__))


def check(domain_name):
    """Categorize site with all proxies in proxies folder."""
    # Submit domain to proxy
    for k, v in get_check_proxies().items():
        try:
            driver = webdriver.Chrome(
                executable_path=f"{script_dir}/drivers/chromedriver"
            )
        except OSError:
            driver = webdriver.Chrome(
                executable_path=f"{script_dir}/drivers/chromedriver.exe"
            )
        try:
            resp = v(driver, domain_name)
            print(f"{k} responsed with {resp}")
            time.sleep(3)
        except Exception as e:
            print(str(e))
        finally:
            driver.quit()


domain_name = input("Enter a domain name: ")
check(domain_name)
