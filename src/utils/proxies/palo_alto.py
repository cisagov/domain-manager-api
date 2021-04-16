"""Palo alto categorization."""
# Standard Python Libraries
import time

# Third-Party Libraries
from selenium.webdriver.common.by import By

# cisagov Libraries
from utils.proxies.captcha import get_and_solve


def categorize(driver, domain, category, two_captcha_api_key):
    """Categorize with palo alto."""
    print("Running Palo Alto proxy")
    driver.get("https://urlfiltering.paloaltonetworks.com/")
    driver.set_window_size(1518, 804)
    driver.find_element(By.ID, "id_url").click()
    driver.find_element(By.ID, "id_url").send_keys(f"http://{domain}")
    get_and_solve(
        driver, two_captcha_api_key, "https://urlfiltering.paloaltonetworks.com/"
    )
    driver.switch_to.default_content()
    driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    driver.find_element(By.ID, "myLink").click()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, ".fa-plus-square").click()
    time.sleep(1)
    driver.find_element(By.ID, "searchInput").click()
    driver.find_element(By.ID, "searchInput").send_keys(category)
    time.sleep(1)
    driver.find_element(
        By.CSS_SELECTOR, ".cate-list-group-item:nth-child(23) > p"
    ).click()
    driver.find_element(By.ID, "id_comment").click()
    driver.find_element(By.ID, "id_comment").send_keys("Test Comment")
    driver.find_element(By.ID, "id_your_email").send_keys("idahotester33@gmail.com")
    driver.find_element(By.ID, "id_confirm_email").send_keys("idahotester33@gmail.com")
    get_and_solve(
        driver, two_captcha_api_key, "https://urlfiltering.paloaltonetworks.com/"
    )
    driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()


def check_category(driver, domain, category, two_captcha_api_key):
    """Check domain category on Palo Alto."""
    pass
