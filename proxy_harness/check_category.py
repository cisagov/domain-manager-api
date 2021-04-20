"""Categorization controller. Mac and linux compatible."""
# Standard Python Libraries
import os

# Third-Party Libraries
from selenium import webdriver
import undetected_chromedriver as uc

# cisagov Libraries
from utils.proxies import PROXIES

# Load environment variables from .env file
script_dir = os.path.dirname(os.path.realpath(__file__))


def check(domain_name):
    """Categorize site with all proxies in proxies folder."""
    category_results = []

    # Submit domain to proxies via selenium
    for proxy in PROXIES:
        if proxy.get("check_url"):
            category = process(proxy.get("check_category_func"), domain_name)
            data = {
                "proxy": proxy["name"],
                "check_url": proxy.get("check_url"),
                "category": category,
            }
            category_results.append(data)


def process(proxy_func, domain_name):
    """Check a category against each proxy."""
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    # Set driver
    try:
        driver = uc.Chrome(
            executable_path=f"{script_dir}/drivers/chromedriver",
            options=options,
        )
    except OSError:
        driver = uc.Chrome(
            executable_path=f"{script_dir}/drivers/chromedriver.exe",
            options=options,
        )

    # Check category
    try:
        category = proxy_func(driver, domain_name)
        return category
    except Exception as e:
        print(str(e))
        return None
    finally:
        driver.quit()


domain_name = input("Enter a domain name: ")
check(domain_name)
