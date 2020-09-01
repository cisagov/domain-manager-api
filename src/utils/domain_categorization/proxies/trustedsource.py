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

from utils.domain_categorization.driver import driver


driver.set_page_load_timeout(5)


def submit_url(domain):
    """Submit domain to McAfee's trustedsource.org."""
    domain = domain[:-1]
    try:
        driver.get("https://www.trustedsource.org/")
    except TimeoutException:
        driver.quit()
        return
    driver.set_window_size(2061, 1265)
    driver.find_element(By.NAME, "product").click()
    dropdown = driver.find_element(By.NAME, "product")
    dropdown.find_element(By.XPATH, "//option[. = 'McAfee Real-Time Database']").click()
    driver.find_element(By.NAME, "url").click()
    driver.find_element(By.NAME, "url").send_keys(f"http://{domain}")
    driver.find_element(By.CSS_SELECTOR, "td > .button > input").click()
    driver.find_element(By.CSS_SELECTOR, "td > .button > input").click()
    driver.find_element(By.NAME, "cat_1").click()
    dropdown = driver.find_element(By.NAME, "cat_1")
    dropdown.find_element(By.XPATH, "//option[. = 'Health']").click()
    driver.find_element(By.CSS_SELECTOR, ".button:nth-child(10) > input").click()
    success_msg = driver.find_element(By.CSS_SELECTOR, "h2").text

    return success_msg
