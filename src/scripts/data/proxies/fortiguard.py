# mypy: ignore-errors
# flake8: noqa
from selenium.webdriver.common.by import By


driver.get(url)
driver.set_window_size(1058, 979)
driver.find_element(By.ID, "web_filter_rating_info_form_url").click()
driver.find_element(By.ID, "web_filter_rating_info_form_url").send_keys(
    f"http://{domain}"
)
driver.find_element(By.ID, "web_filter_rating_info_form_categorysuggestion").click()
dropdown = driver.find_element(By.ID, "web_filter_rating_info_form_categorysuggestion")
dropdown.find_element(By.XPATH, "//option[. = 'Health and Wellness']").click()
driver.find_element(By.ID, "web_filter_rating_info_form_name").click()
driver.find_element(By.ID, "web_filter_rating_info_form_name").send_keys("INL")
driver.find_element(By.ID, "web_filter_rating_info_form_email").send_keys(
    "test@inltesting.xyz"
)
driver.find_element(By.ID, "web_filter_rating_info_form_companyname").click()
driver.find_element(By.ID, "web_filter_rating_info_form_companyname").send_keys(
    "INL Testing"
)
driver.find_element(By.CSS_SELECTOR, ".page-section > .row:nth-child(2)").click()
driver.switch_to.frame(0)
driver.find_element(By.CSS_SELECTOR, ".recaptcha-checkbox-border").click()
driver.switch_to.default_content()
driver.find_element(By.ID, "web_filter_rating_info_form_submit").click()
