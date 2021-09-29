"""Trusted Source Categorization."""
# Third-Party Libraries
from bs4 import BeautifulSoup
import requests  # type: ignore
from selenium.webdriver.common.by import By


def categorize(driver, domain, category, two_captcha_api_key):
    """Categorize with Trusted Source."""
    print("Running McAfee Trusted Source proxy")
    driver.get("https://trustedsource.org/")
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
    dropdown.find_element(By.XPATH, f"//option[. = '{category}']").click()
    driver.find_element(By.CSS_SELECTOR, ".button:nth-child(10) > input").click()
    driver.find_element(By.CSS_SELECTOR, "h2").text


def check_category(driver, domain):
    """Check domain category on McAfee trusted source."""
    print("Checking McAfee Trusted Source proxy")
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
    }
    session.headers.update(headers)
    base_check = "http://www.trustedsource.org/sources/index.pl"
    r = session.get(base_check)
    bs = BeautifulSoup(r.text, "html.parser")
    form = bs.find("form", {"class": "contactForm"})
    e = form.find("input", {"name": "e"}).get("value")
    c = form.find("input", {"name": "c"}).get("value")

    headers["Referer"] = base_check
    session.headers.update(headers)
    payload = {
        "sid": (None, ""),
        "e": (None, e),
        "c": (None, c),
        "p": (None, ""),
        "action": (None, "checksingle"),
        "product": (None, "13-ts-3"),
        "url": (None, domain),
    }
    response = session.post(
        "https://www.trustedsource.org/en/feedback/url", headers=headers, files=payload
    )
    bs = BeautifulSoup(response.content, "html.parser")
    form = bs.find("form", {"class": "contactForm"})
    results_table = bs.find("table", {"class": "result-table"})
    td = results_table.find_all("td")
    return td[len(td) - 2].text
