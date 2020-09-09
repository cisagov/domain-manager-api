"""Categorization controller."""
# Third-Party Libraries
from api.documents.active_site import ActiveSite
from api.documents.proxy import Proxy
from utils.domain_categorization.driver import driver
from flask import current_app


def categorization_manager(live_site_id):
    """Manage categorization of active sites."""
    active_site = ActiveSite.get_by_id(live_site_id)
    domain = active_site.get("domain").get("Name")
    if active_site.get("is_categorized"):
        return {"Error": f"{domain} has already been categorized."}

    # Submit domain to proxy
    if not current_app.config["TESTING"]:
        proxies = Proxy.get_all()
        for proxy in proxies:
            try:
                exec(
                    proxy.get("script").decode(),
                    {"driver": driver, "domain": proxy.get("url")},
                )
            except Exception as err:
                return {"error": str(err)}

    # Update database
    ActiveSite.update(live_site_id=live_site_id, is_categorized=True)
    return {"message": f"{domain} has been categorized"}
