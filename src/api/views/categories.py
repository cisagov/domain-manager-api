"""Category Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView
from selenium import webdriver

# cisagov Libraries
from api.views import CATEGORIES
from settings import BROWSERLESS_ENDPOINT, TWO_CAPTCHA_API_KEY, logger
from utils.proxies.proxies import get_categorize_proxies, get_check_proxies


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

    def post(self, domain_name):
        """Categorize an external domain."""
        category = [
            category
            for category in CATEGORIES
            if category["name"] == request.json.get("category", "").title()
        ][0]

        resp = []
        for k, v in get_categorize_proxies().items():
            proxy_category = "".join(
                detail.get(k) for detail in category.get("proxies") if k in detail
            )
            driver = self.driver()
            driver.set_page_load_timeout(60)
            try:
                categorize = v(
                    driver=driver,
                    domain=domain_name,
                    category=proxy_category,
                    two_captcha_api_key=TWO_CAPTCHA_API_KEY,
                )
                resp.append(categorize)
                driver.quit()
            except Exception as e:
                self.driver().quit()
                logger.exception(e)
        return jsonify(resp)
