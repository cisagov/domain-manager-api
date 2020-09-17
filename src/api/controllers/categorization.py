"""Categorization controller."""
import os

# Third-Party Libraries
from api.documents.active_site import ActiveSite
from api.documents.proxy import Proxy
from selenium import webdriver
from flask import current_app


browserless_endpoint = os.environ.get("BROWSERLESS_ENDPOINT")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")

driver = webdriver.Remote(
    command_executor=f"http://{browserless_endpoint}/webdriver",
    desired_capabilities=chrome_options.to_capabilities(),
)


def categorization_manager(live_site_id):
    """Manage categorization of active sites."""
    active_site = ActiveSite.get_by_id(live_site_id)
    domain = active_site.get("domain").get("Name")
    domain_url = domain[:-1]
    if active_site.get("is_categorized"):
        return {"Error": f"{domain} has already been categorized."}

    # Submit domain to proxy
    if not current_app.config["TESTING"]:
        proxies = Proxy.get_all()
        for proxy in proxies:
            try:
                exec(
                    proxy.get("script").decode(),
                    {"driver": driver, "url": proxy.get("url"), "domain": domain_url},
                )
            except Exception as err:
                driver.quit()
                return {"error": str(err)}

    # Quit WebDriver
    driver.quit()

    # Update database
    ActiveSite.update(live_site_id=live_site_id, is_categorized=True)
    return {"message": f"{domain} has been categorized"}
