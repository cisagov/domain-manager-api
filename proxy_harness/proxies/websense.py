"""Websense categorization check."""
# Standard Python Libraries
import re
import time
import urllib

# Third-Party Libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def req_check():
    """Check requests for the day."""
    request = urllib.request.Request("http://csi.websense.com")
    request.add_header(
        "User-Agent", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)"
    )
    # Bandit complains that url is not being audited as it will open file:/ or custom schemes.
    # Only an http scheme is being opened and so there is nothing to worry about.
    # https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b310-urllib-urlopen
    response = urllib.request.urlopen(request)  # nosec
    resp = response.read().decode("utf-8")
    num_remaining = re.findall('reports">(.*?) report', resp, re.DOTALL)[0]
    return num_remaining


def check_category(driver, domain):
    """Check domain category on Websense."""
    print("Checking Websense proxy")
    num_remaining = "1"
    print("Forcepoint: You have " + num_remaining + " requests left for the day.")
    if int(num_remaining) > 0:
        driver.get("http://csi.websense.com/")
        driver.set_window_size(1765, 1040)
        driver.find_element(By.ID, "LookupUrl").click()
        driver.find_element(By.ID, "LookupUrl").send_keys(f"http://{domain}")
        driver.find_element(By.ID, "LookupUrl").send_keys(Keys.ENTER)
        time.sleep(2)
        category = driver.find_element_by_xpath("//td[@class='classAction']")

        return category.text
    else:
        return "No requests remaining for this IP."
