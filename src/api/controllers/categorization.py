"""Categorization controller."""
# Third-Party Libraries
from api.documents.active_site import ActiveSite
from flask import current_app


def categorization_manager(live_site_id):
    """Manage categorization of active sites."""
    active_site = ActiveSite.get_by_id(live_site_id)
    domain = active_site.get("domain").get("Name")
    if active_site.get("is_categorized"):
        return {"Error": f"{domain} has already been categorized."}

    # Submit domain to trusted source proxy
    # if not current_app.config["TESTING"]:
    #     try:
    #         trustedsource.submit_url(domain)
    #     except Exception:
    #         return {"error": f"can not categorize {domain} at this time."}

    # Update database
    ActiveSite.update(live_site_id=live_site_id, is_categorized=True)
    return {"message": f"{domain} has been categorized"}
