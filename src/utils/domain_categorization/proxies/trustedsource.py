"""McAfee proxy."""
# Standard Python Libraries
import os
import json
import time

# Third-Party Libraries
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

browserless_endpoint = os.environ.get("BROWSERLESS_ENDPOINT")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")

proxy_driver = webdriver.Remote(
    command_executor=f"http://{browserless_endpoint}/webdriver",
    desired_capabilities=chrome_options.to_capabilities(),
)
proxy_driver.set_page_load_timeout(5)


def submit_url(domain):
    """Submit domain to McAfee's trustedsource.org."""
    domain = domain[:-1]
    try:
        proxy_driver.get("https://www.trustedsource.org/")
    except TimeoutException:
        proxy_driver.quit()
        return
    proxy_driver.set_window_size(2061, 1265)
    proxy_driver.find_element(By.NAME, "product").click()
    dropdown = proxy_driver.find_element(By.NAME, "product")
    dropdown.find_element(By.XPATH, "//option[. = 'McAfee Real-Time Database']").click()
    proxy_driver.find_element(By.NAME, "url").click()
    proxy_driver.find_element(By.NAME, "url").send_keys(f"http://{domain}")
    proxy_driver.find_element(By.CSS_SELECTOR, "td > .button > input").click()
    proxy_driver.find_element(By.CSS_SELECTOR, "td > .button > input").click()
    proxy_driver.find_element(By.NAME, "cat_1").click()
    dropdown = proxy_driver.find_element(By.NAME, "cat_1")
    dropdown.find_element(By.XPATH, "//option[. = 'Health']").click()
    proxy_driver.find_element(By.CSS_SELECTOR, ".button:nth-child(10) > input").click()
    success_msg = proxy_driver.find_element(By.CSS_SELECTOR, "h2").text
    proxy_driver.quit()

    return success_msg
