"""Websites controller."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
# Third Party Libraries
import requests

# cisagov Libraries
from api.schemas.website_schema import WebsiteSchema
from models.application import Application
from models.website import Website
from settings import STATIC_GEN_URL
from utils.aws.site_handler import delete_dns, launch_site, setup_dns


def usage_history(website):
    """Update website usage history on application change."""
    update = {"application": website.application, "launch_date": datetime.utcnow()}
    response = website.get().get("history", None)
    if response:
        response.append(update)
    else:
        response = [update]
    return response


def generate_website_manager(request, website_id, category):
    """Generate a website from templates manager."""
    website = Website(_id=website_id)
    website.get()
    domain = website.name

    post_data = request.json

    # Post request to go templates static gen
    resp = requests.post(
        f"{STATIC_GEN_URL}/generate/?category={category}&domain={domain}",
        json=post_data,
    )

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e)}

    return {
        "message": f"{domain} static site has been created from the {category} template."
    }


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
