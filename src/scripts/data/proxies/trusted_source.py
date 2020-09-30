# mypy: ignore-errors
# flake8: noqa
# Third-Party Libraries
from selenium.webdriver.common.by import By

driver.get(url)
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
dropdown.find_element(By.XPATH, "//option[. = 'Health']").click()
driver.find_element(By.CSS_SELECTOR, ".button:nth-child(10) > input").click()
success_msg = driver.find_element(By.CSS_SELECTOR, "h2").text
