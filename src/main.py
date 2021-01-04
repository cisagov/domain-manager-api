"""Domain manager."""
# Third-Party Libraries
from flask import Flask, render_template
from flask_cors import CORS

# cisagov Libraries
from api.views.applications import ApplicationsView, ApplicationView
from api.views.categories import CategoriesView, CategorizeView, CheckCategoriesView
from api.views.email_address import EmailAddressView
from api.views.hosted_zones import HostedZonesView
from api.views.proxies import ProxiesView, ProxyView
from api.views.templates import TemplatesView, TemplateView
from api.views.websites import (
    WebsiteGenerateView,
    WebsiteLaunchView,
    WebsiteRedirectView,
    WebsitesView,
    WebsiteView,
)
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
    ("/categorize/<website_id>/", CategorizeView),
    ("/check/", CheckCategoriesView),
    ("/proxies/", ProxiesView),
    ("/proxy/<proxy_id>/", ProxyView),
    ("/templates/", TemplatesView),
    ("/template/<template_id>/", TemplateView),
    ("/websites/", WebsitesView),
    ("/website/<website_id>/", WebsiteView),
    ("/website/<website_id>/generate/", WebsiteGenerateView),
    ("/website/<website_id>/redirect/", WebsiteRedirectView),
    ("/website/<website_id>/launch/", WebsiteLaunchView),
]

for rule in rules:
    url = f"{url_prefix}{rule[0]}"
    rule[1].decorators = [auth_required]
    app.add_url_rule(url, view_func=rule[1].as_view(url))


@app.route("/")
def api_map():
    """List endpoints for api."""
    endpoints = {
        endpoint.rule: endpoint.methods
        for endpoint in app.url_map.__dict__["_rules"]
        if endpoint.rule not in ["/static/<path:filename>", "/"]
    }
    return render_template("index.html", endpoints=endpoints)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
