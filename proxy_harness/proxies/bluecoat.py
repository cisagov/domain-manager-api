# mypy: ignore-errors
# flake8: noqa
# Standard Python Libraries
import time

# Third-Party Libraries
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def check_submitted():
    if len(is_submitted_msg) > 0:
        print("Already been Submitted")
        return
    return


print("Running Bluecoat proxy")
driver.get("https://sitereview.bluecoat.com/")
driver.set_window_size(1765, 1040)
driver.find_element(By.ID, "txtUrl").click()
driver.find_element(By.ID, "txtUrl").send_keys(f"http://{domain}")
driver.find_element(By.ID, "txtUrl").send_keys(Keys.ENTER)
time.sleep(1)
is_submitted_msg = driver.find_elements_by_xpath(
    "//*[contains(text(),'Only a single submission per site is needed unless the content differs')]"
)
check_submitted()
filter_dropdown = driver.find_element(By.CSS_SELECTOR, "#selFilteringService input")
filter_dropdown.click()
filtering_service = filter_dropdown.find_element_by_xpath(
    "//*[contains(text(),'Blue Coat ProxyClient')]"
)
filtering_service.click()
category_dropdown = driver.find_element(By.CSS_SELECTOR, "#txtCat1 input")
category_dropdown.click()
category_name = category_dropdown.find_element_by_xpath(
    "//*[contains(text(),'Health')]"
)
scroll_to_category = ActionChains(driver).move_to_element(category_name)
scroll_to_category.perform()
category_name.click()
driver.find_element(By.ID, "email").click()
driver.find_element(By.ID, "email").send_keys("idahotester33@gmail.com")
driver.find_element(By.ID, "emailcc").send_keys("idahotester33@gmail.com")
time.sleep(1)
driver.find_element(By.ID, "submit2").click()
