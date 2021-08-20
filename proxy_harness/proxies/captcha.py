"""Captcha helpers."""
# Standard Python Libraries
import time

# Third-Party Libraries
from selenium.webdriver.common.by import By
from twocaptcha import TwoCaptcha


def get_and_solve(driver, two_captcha_api_key, url):
    """Get and solve captcha element."""
    recaptcha_element = driver.find_element(By.CLASS_NAME, "g-recaptcha")
    sitekey = recaptcha_element.get_attribute("data-sitekey")

    solver = TwoCaptcha(two_captcha_api_key)
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
