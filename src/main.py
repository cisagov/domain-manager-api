"""Domain manager."""
# Standard Python Libraries
from datetime import date

# Third-Party Libraries
from flask import Flask, render_template
from flask.json import JSONEncoder
from flask_cors import CORS

# cisagov Libraries
from api.views.applications import ApplicationsView, ApplicationView
from api.views.categories import CategoriesView, CategoryCheckView
from api.views.email_address import EmailAddressView
from api.views.hosted_zones import HostedZonesView
from api.views.proxies import ProxiesView, ProxyView
from api.views.templates import (
    TemplateAttributesView,
    TemplateContentView,
    TemplatesView,
    TemplateView,
)
from api.views.websites import (
    WebsiteCategorizeView,
    WebsiteContentView,
    WebsiteGenerateView,
    WebsiteLaunchView,
    WebsiteRecordView,
    WebsiteRedirectView,
    WebsitesView,
    WebsiteView,
)
from settings import logger
from utils.decorators.auth import auth_required

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# register apps
url_prefix = "/api"

rules = [
    ("/applications/", ApplicationsView),
    ("/application/<application_id>/", ApplicationView),
    ("/generate-dns/", HostedZonesView),
    ("/generate-email-address/", EmailAddressView),
    ("/categories/", CategoriesView),
    ("/check/", CategoryCheckView),
    ("/proxies/", ProxiesView),
    ("/proxy/<proxy_id>/", ProxyView),
    ("/templates/", TemplatesView),
    ("/template/<template_id>/", TemplateView),
    ("/template/<template_id>/content/", TemplateContentView),
    ("/templates/attributes/", TemplateAttributesView),
    ("/websites/", WebsitesView),
    ("/website/<website_id>/", WebsiteView),
    ("/website/<website_id>/categorize/", WebsiteCategorizeView),
    ("/website/<website_id>/content/", WebsiteContentView),
    ("/website/<website_id>/generate/", WebsiteGenerateView),
    ("/website/<website_id>/redirect/", WebsiteRedirectView),
    ("/website/<website_id>/launch/", WebsiteLaunchView),
    ("/website/<website_id>/records/", WebsiteRecordView),
]

for rule in rules:
    url = f"{url_prefix}{rule[0]}"
    rule[1].decorators = [auth_required]
    app.add_url_rule(url, view_func=rule[1].as_view(url))


class CustomJSONEncoder(JSONEncoder):
    """CustomJSONEncoder."""

    def default(self, obj):
        """Encode datetime properly."""
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


app.json_encoder = CustomJSONEncoder


@app.route("/")
def api_map():
    """List endpoints for api."""
    logger.info("API is up and running.")
    endpoints = {
        endpoint.rule: endpoint.methods
        for endpoint in app.url_map.__dict__["_rules"]
        if endpoint.rule not in ["/static/<path:filename>", "/"]
    }
    return render_template("index.html", endpoints=endpoints)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
