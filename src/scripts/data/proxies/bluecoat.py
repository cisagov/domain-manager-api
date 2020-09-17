# mypy: ignore-errors
# flake8: noqa
from selenium.webdriver.common.by import By


driver.get(url)
driver.set_window_size(1765, 1040)
driver.find_element(By.ID, "txtUrl").click()
driver.find_element(By.ID, "txtUrl").send_keys(f"http://{domain}")
driver.find_element(By.ID, "btnLookup").click()
driver.find_element(By.CSS_SELECTOR, "#selFilteringService input").click()
driver.find_element(By.CSS_SELECTOR, "#a2a3338920fd > .ng-option-label").click()
driver.find_element(By.CSS_SELECTOR, "#txtCat1 > .ng-select-container").click()
driver.find_element(By.ID, "abb278bc7673").click()
driver.find_element(By.ID, "email").click()
driver.find_element(By.ID, "email").send_keys("test@inltesting.xyz")
driver.find_element(By.ID, "emailcc").send_keys("test@inltesting.xyz")
driver.find_element(By.ID, "submit2").click()
