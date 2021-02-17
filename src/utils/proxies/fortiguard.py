"""Fortiguard Categorization."""
# Third-Party Libraries
from selenium.webdriver.common.by import By

# cisagov Libraries
from utils.proxies.captcha import get_and_solve


def categorize(driver, domain, category, two_captcha_api_key):
    """Categorize with fortiguard."""
    driver.get("https://www.fortiguard.com/faq/wfratingsubmit")
    driver.set_window_size(1108, 1039)
    driver.find_element(By.ID, "__agreementButton").click()
    driver.find_element(By.ID, "web_filter_rating_info_form_url").click()
    driver.find_element(By.ID, "web_filter_rating_info_form_url").send_keys(
        f"http://{domain}"
    )
    driver.find_element(By.ID, "web_filter_rating_info_form_categorysuggestion").click()
    dropdown = driver.find_element(
        By.ID, "web_filter_rating_info_form_categorysuggestion"
    )
    dropdown.find_element(By.XPATH, f"//option[. = '{category}']").click()
    driver.find_element(By.ID, "web_filter_rating_info_form_name").click()
    driver.find_element(By.ID, "web_filter_rating_info_form_name").send_keys(
        "Idaho Labs"
    )
    driver.find_element(By.ID, "web_filter_rating_info_form_email").click()
    driver.find_element(By.ID, "web_filter_rating_info_form_email").send_keys(
        "idahotester33@gmail.com"
    )
    driver.find_element(By.ID, "web_filter_rating_info_form_companyname").click()
    driver.find_element(By.ID, "web_filter_rating_info_form_companyname").send_keys(
        "IDAHO LABS"
    )

    get_and_solve(
        driver, two_captcha_api_key, "https://www.fortiguard.com/faq/wfratingsubmit"
    )
    driver.find_element(By.ID, "web_filter_rating_info_form_submit").click()


def check_category(driver, domain):
    """Check domain category on Fortiguard."""
    print("Checking Fortiguard proxy")
    driver.get(f"https://www.fortiguard.com/webfilter?q={domain}&version=8")
    category = driver.find_element_by_xpath("//h4[@class='info_title']")
    return category.text.replace("Category: ", "")
