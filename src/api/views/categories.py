"""Category Views."""
# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView
from selenium import webdriver

# cisagov Libraries
from api.views import CATEGORIES
from settings import BROWSERLESS_ENDPOINT, logger
from utils.proxies.proxies import get_check_proxies


class CategoriesView(MethodView):
    """CategoriesView."""

    def get(self):
        """Get all categories."""
        return jsonify(CATEGORIES)


class ExternalCategoriesView(MethodView):
    """External Categories View."""

    def driver(self):
        """Headless Chrome Driver."""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")

        return webdriver.Remote(
            command_executor=f"http://{BROWSERLESS_ENDPOINT}/webdriver",
            desired_capabilities=chrome_options.to_capabilities(),
        )

    def get(self, domain_name):
        """Check categories for external domains."""
        resp = []
        for k, v in get_check_proxies().items():
            driver = self.driver()
            driver.set_page_load_timeout(60)
            try:
                category = v(
                    driver,
                    domain_name,
                )
                resp.append({k: category})
            except Exception as e:
                self.driver().quit()
                logger.exception(e)

        return jsonify(resp)
