"""Categorization controller. Mac and linux compatible."""
# Standard Python Libraries
import os
import time

# Third-Party Libraries
import undetected_chromedriver as webdriver

# cisagov Libraries
from proxy_harness.proxies import CATEGORIES, PROXIES

# Load environment variables from .env file
script_dir = os.path.dirname(os.path.realpath(__file__))
api_key = os.getenv("TWO_CAPTCHA")


def categorize(requested_category, domain_name):
    """Categorize a domain across proxies."""
    category = CATEGORIES.get(requested_category.title())

    category_results = []

    for proxy in PROXIES:
        if proxy.get("categorize_url"):
            proxy_category = category.get(proxy["name"])
            categorize_response = process(
                proxy_func=proxy.get("categorize_func"),
                proxy_category=proxy_category,
                domain_name=domain_name,
            )
            data = {
                "proxy": proxy["name"],
                "submitted_category": proxy_category,
                "is_submitted": categorize_response,
                "categorize_url": proxy.get("categorize_url"),
            }
            category_results.append(data)

    return category_results


def process(proxy_func, proxy_category, domain_name):
    """Categorize site with all proxies in proxies folder."""
    try:
        driver = webdriver.Chrome(executable_path=f"{script_dir}/drivers/chromedriver")
    except OSError:
        driver = webdriver.Chrome(
            executable_path=f"{script_dir}/drivers/chromedriver.exe"
        )

    try:
        proxy_func(
            driver=driver,
            domain=domain_name,
            category=proxy_category,
            two_captcha_api_key=api_key,
        )
        time.sleep(3)
    except Exception as e:
        print(str(e))
    finally:
        driver.quit()

    # Quit WebDriver
    print(f"{domain_name} has been categorized")


domain_name = input("Enter a domain name: ")
category_name = input("Enter a category: ")
categorize(category_name, domain_name)
