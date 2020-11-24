"""Websites controller."""
from datetime import datetime

# Third-Party Libraries
from models.application import Application
from models.website import Website
from api.schemas.website_schema import WebsiteSchema
from utils.aws.site_handler import delete_site, launch_site, setup_dns, delete_dns


def usage_history(website):
    """Update website usage history on application change."""
    update = {"application": website.application, "launch_date": datetime.utcnow()}
    response = website.get().get("history", None)
    if response:
        response.append(update)
    else:
        response = [update]
    return response


def website_manager(request, website_id=None):
    """Manage websites."""
    if not website_id:
        website_schema = WebsiteSchema(many=True)
        response = website_schema.dump(Website().all())
        return response

    website = Website(_id=website_id)
    if request.method == "PUT":
        put_data = request.json
        app_name = put_data.get("application", None)
        if app_name:
            application = Application()
            application.name = put_data["application"]
            website.application = application.get()
            website.history = usage_history(website)
        website.update()
        response = {"message": "Active site has been updated."}
    else:
        active_site_schema = WebsiteSchema()
        response = active_site_schema.dump(website.get())

    return response
