"""ChromeDriver for Categorization."""
# Third-Party Libraries
from selenium import webdriver

# cisagov Libraries
from settings import BROWSERLESS_ENDPOINT


def get_driver():
    """Get chromedriver for checking and categorizing."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    return webdriver.Remote(
        command_executor=f"http://{BROWSERLESS_ENDPOINT}/webdriver",
        desired_capabilities=chrome_options.to_capabilities(),
    )
