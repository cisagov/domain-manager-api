"""Fortiguard Categorization."""
# Standard Python Libraries
import re
import urllib

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


def check_category(domain):
    """Check domain category on Fortiguard."""
    request = urllib.request.Request("https://fortiguard.com/webfilter?q=" + domain)
    request.add_header(
        "User-Agent", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)"
    )
    request.add_header("Origin", "https://fortiguard.com")
    request.add_header("Referer", "https://fortiguard.com/webfilter")
    response = urllib.request.urlopen(request)
    try:
        resp = response.read().decode("utf-8")
        cat = re.findall('Category: (.*?)" />', resp, re.DOTALL)
        print("\033[1;32m[!] Site categorized as: " + cat[0] + "\033[0;0m")
        return cat[0]
    except Exception as e:
        print("An error occurred")
        print(e)
        return None
