"""Categorization controller."""
import os
import logging
from bson.son import SON

# Third-Party Libraries
from models.website import Website
from models.proxy import Proxy
from models.categories import Category
from api.schemas.category_schema import CategorySchema
from utils.two_captcha import two_captcha_api_key
from selenium import webdriver
from flask import current_app
from selenium.webdriver.common.by import By

browserless_endpoint = os.environ.get("BROWSERLESS_ENDPOINT")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def categories_manager():
    """Manage categories types."""
    categories = Category().all()
    category_schema = CategorySchema(many=True)
    return category_schema.dump(categories)


def categorization_manager(live_site_id, category):
    """Manage categorization of active sites."""
    active_site = Website(_id=live_site_id).get()
    domain = active_site.get("domain").get("Name")
    domain_url = domain[:-1]
    if active_site.get("is_categorized"):
        return {"error": f"{domain} has already been categorized."}

    # Get all categories
    categories = Category().all()
    category_names = [category.get("name") for category in categories]

    if category not in category_names:
        return {"error": "Category does not exist"}

    is_submitted = []
    # Submit domain to proxy
    if not current_app.config["TESTING"]:
        proxies = Proxy().all()
        for proxy in proxies:
            proxy_name = proxy["name"]

            # Get unique category name for each proxy
            proxy_category = "".join(
                detail.get(proxy_name)
                for detail in Category().get(category).get("proxies")
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
                    {"_id": proxy["_id"], "name": proxy_name, "is_categorized": False}
                )
                logger.info(f"Categorized with {proxy_name}")
            except Exception as err:
                driver.quit()
                logger.error(f"{proxy_name} has failed")
                return {"error": str(err)}

    # Quit WebDriver
    driver.quit()

    # Update database
    Website.update(live_site_id=live_site_id, is_submitted=is_submitted)
    return {"message": f"{domain} has been successfully categorized"}
