"""Trend Micro categorization."""
# Standard Python Libraries
import time

# Third-Party Libraries
from selenium.webdriver.common.by import By

# cisagov Libraries
from utils.proxies.captcha import get_and_solve


def categorize(driver, domain, category, two_captcha_api_key):
    """Categorize with Trend Micro."""
    print("Running Trend Micro proxy")
    driver.get("https://global.sitesafety.trendmicro.com/")
    driver.set_window_size(2576, 1416)
    driver.find_element(By.ID, "urlname").click()
    driver.find_element(By.ID, "urlname").send_keys(f"http://{domain}")
    driver.find_element(By.ID, "getinfo").click()
    driver.find_element(By.ID, "myBtn").click()
    driver.find_element(By.CSS_SELECTOR, ".modal_content_2:nth-child(2) a").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".lightbg:nth-child(4) input").click()
    driver.find_element(By.CSS_SELECTOR, ".suggestoption > .radioinput").click()
    driver.find_element(By.ID, "radio5").click()
    category_dropdown = driver.find_element_by_xpath("//*[contains(text(),'General')]")
    time.sleep(1)
    category_dropdown.click()
    category_button = category_dropdown.find_element_by_xpath(
        f"//input[@value='{category}']"
    )
    time.sleep(1)
    category_button.click()
    time.sleep(1)
    driver.find_element(By.ID, "owner").click()
    driver.find_element(By.ID, "comments").click()
    driver.find_element(By.ID, "comments").send_keys("Changing Website for customer")
    driver.find_element(By.ID, "textfieldemail").send_keys("idahotester33@gmail.com")
    get_and_solve(
        driver, two_captcha_api_key, "https://global.sitesafety.trendmicro.com/"
    )
    driver.find_element(By.NAME, "send").click()
    driver.find_element(By.LINK_TEXT, "Check a URL").click()
