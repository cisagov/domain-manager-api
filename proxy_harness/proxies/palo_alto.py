# mypy: ignore-errors
# flake8: noqa
# Standard Python Libraries
import json
import os
import sys
import time

# Third-Party Libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from twocaptcha import TwoCaptcha


def get_and_solve(url):
    recaptcha_element = driver.find_element(By.CLASS_NAME, "g-recaptcha")
    sitekey = recaptcha_element.get_attribute("data-sitekey")

    solver = TwoCaptcha(api_key)
    try:
        result = solver.recaptcha(sitekey=sitekey, url=url)

    except Exception as e:
        print(e)
    else:
        driver.execute_script(
            "document.getElementById('g-recaptcha-response').innerHTML='"
            + result["code"]
            + "';"
        )
        time.sleep(3)


print("Running Palo Alto proxy")
driver.get("https://urlfiltering.paloaltonetworks.com/")
driver.set_window_size(1518, 804)
driver.find_element(By.ID, "id_url").click()
driver.find_element(By.ID, "id_url").send_keys(f"http://{domain}")
get_and_solve("https://urlfiltering.paloaltonetworks.com/")
driver.switch_to.default_content()
driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
driver.find_element(By.ID, "myLink").click()
time.sleep(3)
driver.find_element(By.CSS_SELECTOR, ".fa-plus-square").click()
time.sleep(1)
driver.find_element(By.ID, "searchInput").click()
driver.find_element(By.ID, "searchInput").send_keys("Health and Medicine")
time.sleep(1)
driver.find_element(By.CSS_SELECTOR, ".cate-list-group-item:nth-child(23) > p").click()
driver.find_element(By.ID, "id_comment").click()
driver.find_element(By.ID, "id_comment").send_keys("Test Comment")
driver.find_element(By.ID, "id_your_email").send_keys("idahotester33@gmail.com")
driver.find_element(By.ID, "id_confirm_email").send_keys("idahotester33@gmail.com")
get_and_solve("https://urlfiltering.paloaltonetworks.com/")
driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
