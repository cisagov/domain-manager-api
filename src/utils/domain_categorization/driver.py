"""Selenium driver."""
# Standard Python Libraries
import os

# Third-Party Libraries
from selenium import webdriver

browserless_endpoint = os.environ.get("BROWSERLESS_ENDPOINT")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")

driver = webdriver.Remote(
    command_executor=f"http://{browserless_endpoint}/webdriver",
    desired_capabilities=chrome_options.to_capabilities(),
)

driver.set_page_load_timeout(5)
