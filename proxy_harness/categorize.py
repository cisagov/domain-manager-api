"""Categorization controller. Mac and linux compatible."""
# Standard Python Libraries
import os
import time

# Third-Party Libraries
from dotenv import load_dotenv
from selenium import webdriver

# cisagov Libraries
from utils.proxies.proxies import get_categorize_proxies

# Load environment variables from .env file
script_dir = os.path.dirname(os.path.realpath(__file__))
load_dotenv(dotenv_path=f"{script_dir}/../.env")
api_key = os.getenv("TWO_CAPTCHA")


def categorization_manager(domain_url, category_name):
    """Categorize site with all proxies in proxies folder."""
    # Submit domain to proxy
    for k, v in get_categorize_proxies().items():
        try:
            driver = webdriver.Chrome(
                executable_path=f"{script_dir}/drivers/chromedriver"
            )
        except OSError:
            driver = webdriver.Chrome(
                executable_path=f"{script_dir}/drivers/chromedriver.exe"
            )

        try:
            v(driver, domain_url, category_name, api_key)
            time.sleep(3)
        except Exception as e:
            print(str(e))
        finally:
            driver.quit()

    # Quit WebDriver
    print(f"{domain_url} has been categorized")


domain_name = input("Enter a domain name: ")
category_name = input("Enter a category: ")
categorization_manager(domain_name, category_name)
