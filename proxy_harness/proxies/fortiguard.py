# mypy: ignore-errors
# flake8: noqa
# Standard Python Libraries
import os
import time

# Third-Party Libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from twocaptcha import TwoCaptcha

print("Running Fortiguard proxy")
driver.get("https://www.fortiguard.com/faq/wfratingsubmit")
driver.set_window_size(1680, 979)
driver.find_element(By.ID, "__agreementButton").click()
time.sleep(3)
driver.find_element(By.ID, "web_filter_rating_info_form_url").click()
driver.find_element(By.ID, "web_filter_rating_info_form_url").click()
driver.find_element(By.ID, "web_filter_rating_info_form_url").send_keys(
    f"http://{domain}"
)
wait = WebDriverWait(driver, 10)
wait.until(
    EC.presence_of_element_located(
        (By.ID, "web_filter_rating_info_form_categorysuggestion")
    )
)
driver.find_element(By.ID, "web_filter_rating_info_form_categorysuggestion").click()
dropdown = driver.find_element(By.ID, "web_filter_rating_info_form_categorysuggestion")
dropdown.find_element(By.XPATH, "//option[. = 'Health and Wellness']").click()
driver.find_element(By.CSS_SELECTOR, ".page-section > .row:nth-child(2)").click()
wait.until(EC.presence_of_element_located((By.ID, "web_filter_rating_info_form_name")))
driver.find_element(By.ID, "web_filter_rating_info_form_name").click()
driver.find_element(By.ID, "web_filter_rating_info_form_name").send_keys("Idaho Tester")
driver.find_element(By.ID, "web_filter_rating_info_form_email").send_keys(
    "idahotester33@gmail.com"
)
driver.find_element(By.ID, "web_filter_rating_info_form_companyname").send_keys("INL")
recaptcha_element = driver.find_element(By.CLASS_NAME, "g-recaptcha")
sitekey = recaptcha_element.get_attribute("data-sitekey")

solver = TwoCaptcha(api_key)
try:
    result = solver.recaptcha(
        sitekey=sitekey, url="https://www.fortiguard.com/faq/wfratingsubmit"
    )

except Exception as e:
    print(e)
else:
    driver.execute_script(
        "document.getElementById('g-recaptcha-response').innerHTML='"
        + result["code"]
        + "';"
    )
    driver.find_element(By.ID, "web_filter_rating_info_form_submit").click()
    time.sleep(3)
