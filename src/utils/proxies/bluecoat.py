"""Blue Coat Proxy Categorization."""
# Standard Python Libraries
import re
import time

# Third-Party Libraries
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def check_submitted(is_submitted_msg):
    """Check if submitted."""
    if len(is_submitted_msg) > 0:
        print("Already been Submitted")
        return True
    return


def categorize(driver, url, domain, category, two_captcha_api_key):
    """Categorize with bluecoat."""
    print("Running Bluecoat proxy")
    driver.get(url)
    driver.set_window_size(1765, 1040)
    driver.find_element(By.ID, "txtUrl").click()
    driver.find_element(By.ID, "txtUrl").send_keys(f"http://{domain}")
    driver.find_element(By.ID, "txtUrl").send_keys(Keys.ENTER)
    time.sleep(1)
    is_submitted_msg = driver.find_elements_by_xpath(
        "//*[contains(text(),'Only a single submission per site is needed unless the content differs')]"
    )
    if check_submitted(is_submitted_msg):
        return
    filter_dropdown = driver.find_element(By.CSS_SELECTOR, "#selFilteringService input")
    filter_dropdown.click()
    filtering_service = filter_dropdown.find_element_by_xpath(
        "//*[contains(text(),'Blue Coat ProxyClient')]"
    )
    filtering_service.click()
    category_dropdown = driver.find_element(By.CSS_SELECTOR, "#txtCat1 input")
    category_dropdown.click()
    category_name = category_dropdown.find_element_by_xpath(
        f"//*[contains(text(),'{category}')]"
    )
    scroll_to_category = ActionChains(driver).move_to_element(category_name)
    scroll_to_category.perform()
    category_name.click()
    driver.find_element(By.ID, "email").click()
    driver.find_element(By.ID, "email").send_keys("idahotester33@gmail.com")
    driver.find_element(By.ID, "emailcc").send_keys("idahotester33@gmail.com")
    time.sleep(1)
    driver.find_element(By.ID, "submit2").click()


def check_category(domain):
    """Check domain category on Bluecoat."""
    print("[*] Checking category for " + domain)
    data = {"url": domain, "captcha": ""}
    headers = {
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)",
        "Origin": "https://sitereview.bluecoat.com",
        "Referer": "https://sitereview.bluecoat.com",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": "aaa",
        "Content-Type": "application/json; charset=utf-8",
    }
    cookies = {"XSRF-TOKEN": "aaa"}
    response = requests.post(
        "http://sitereview.bluecoat.com/resource/lookup",
        headers=headers,
        json=data,
        cookies=cookies,
    )
    try:
        resp = response.text
        cat = re.findall(
            "<name>(.*?)</name></categorization></categorization>", resp, re.DOTALL
        )
        print("\033[1;32m[!] Site categorized as: " + cat[0] + "\033[0;0m")
        return cat[0]
    except Exception as e:
        print("An error occurred")
        print(e)
        return None
