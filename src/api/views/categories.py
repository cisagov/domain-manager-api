"""Category Views."""
# Standard Python Libraries
import logging
import os

# Third-Party Libraries
from flask import current_app, jsonify, request
from flask.views import MethodView
from selenium import webdriver

# cisagov Libraries
from api.manager import CategoryManager, ProxyManager, WebsiteManager
from utils.categorization import (
    bluecoat,
    fortiguard,
    ibmxforce,
    trustedsource,
    websense,
)
from utils.two_captcha import two_captcha_api_key

category_manager = CategoryManager()
proxy_manager = ProxyManager()
website_manager = WebsiteManager()


class CategoriesView(MethodView):
    """CategoriesView."""

    def get(self):
        """Get all categories."""
        return jsonify(category_manager.all())


class CategorizeView(MethodView):
    """CategorizeView."""

    def get(self, website_id):
        """Manage categorization of active sites."""
        browserless_endpoint = os.environ.get("BROWSERLESS_ENDPOINT")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        active_site = website_manager.get(document_id=website_id)
        domain = active_site.get("domain").get("Name")
        domain_url = domain[:-1]
        if active_site.get("is_categorized"):
            return {"error": f"{domain} has already been categorized."}

        category = category_manager.get(
            filter_data={"name": request.args.get("category")}
        )

        if not category:
            return {"error": "Category does not exist"}

        is_submitted = []
        # Submit domain to proxy
        if not current_app.config["TESTING"]:
            proxies = proxy_manager.all()
            for proxy in proxies:
                proxy_name = proxy["name"]

                # Get unique category name for each proxy
                proxy_category = "".join(
                    detail.get(proxy_name)
                    for detail in category.get("proxies")
                    if proxy_name in detail
                )

                try:
                    driver = webdriver.Remote(
                        command_executor=f"http://{browserless_endpoint}/webdriver",
                        desired_capabilities=chrome_options.to_capabilities(),
                    )
                    driver.set_page_load_timeout(60)
                    exec(
                        proxy.get("script").decode(),
                        {
                            "driver": driver,
                            "url": proxy.get("url"),
                            "domain": domain_url,
                            "api_key": two_captcha_api_key,
                            "category": proxy_category,
                        },
                    )
                    driver.quit()
                    is_submitted.append(
                        {
                            "_id": proxy["_id"],
                            "name": proxy_name,
                            "is_categorized": False,
                        }
                    )
                    logging.info(f"Categorized with {proxy_name}")
                except Exception as err:
                    driver.quit()
                    logging.error(f"{proxy_name} has failed")
                    return {"error": str(err)}

        # Quit WebDriver
        driver.quit()

        # Update database
        website_manager.update(
            document_id=website_id, data={"is_submitted": is_submitted}
        )
        return jsonify({"message": f"{domain} has been successfully categorized"})


class CheckCategoriesView(MethodView):
    """CheckCategoriesView."""

    def get(self):
        """Check category for a domain."""
        domain = request.args.get("domain")
        return jsonify(
            {
                "Trusted Source": trustedsource.check_category(domain),
                "Bluecoat": bluecoat.check_category(domain),
                # "Cisco Talos": ciscotalos.check_category(domain),
                "IBM X-Force": ibmxforce.check_category(domain),
                "Fortiguard": fortiguard.check_category(domain),
                "Websense": websense.check_category(domain),
            }
        )
