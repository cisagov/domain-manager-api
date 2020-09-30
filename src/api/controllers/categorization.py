"""Categorization controller."""
import os
from bson.son import SON

# Third-Party Libraries
from api.documents.active_site import ActiveSite
from api.documents.proxy import Proxy
from utils.two_captcha import two_captcha_api_key
from selenium import webdriver
from flask import current_app
from selenium.webdriver.common.by import By

browserless_endpoint = os.environ.get("BROWSERLESS_ENDPOINT")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")


def categorization_manager(live_site_id):
    """Manage categorization of active sites."""
    active_site = ActiveSite.get_by_id(live_site_id)
    domain = active_site.get("domain").get("Name")
    domain_url = domain[:-1]
    if active_site.get("is_categorized"):
        return {"error": f"{domain} has already been categorized."}

    is_submitted = []
    # Submit domain to proxy
    if not current_app.config["TESTING"]:
        proxies = Proxy.get_all()
        for proxy in proxies:
            try:
                driver = webdriver.Remote(
                    command_executor=f"http://{browserless_endpoint}/webdriver",
                    desired_capabilities=chrome_options.to_capabilities(),
                )
                exec(
                    proxy.get("script").decode(),
                    {
                        "driver": driver,
                        "url": proxy.get("url"),
                        "domain": domain_url,
                        "api_key": two_captcha_api_key,
                    },
                )
                driver.quit()
                is_submitted.append(
                    {
                        "_id": proxy["_id"],
                        "name": proxy["name"],
                        "is_categorized": False,
                    }
                )
            except Exception as err:
                driver.quit()
                return {"error": str(err)}

    # Quit WebDriver
    driver.quit()

    # Update database
    ActiveSite.update(live_site_id=live_site_id, is_submitted=is_submitted)
    return {
        "message": f"{domain} has been successfully categorized with Bluecoat, Fortiguard and McAfee"
    }
