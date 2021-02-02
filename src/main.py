"""Domain manager."""
# Standard Python Libraries
from datetime import date

# Third-Party Libraries
from flask import Flask, render_template
from flask.json import JSONEncoder
from flask_cors import CORS
import requests

# cisagov Libraries
from api.views.applications import ApplicationsView, ApplicationView
from api.views.categories import CategoriesView, CategoryCheckView
from api.views.domain_views import (
    DomainCategorizeView,
    DomainCategoryCheckView,
    DomainContentView,
    DomainDeployedCheckView,
    DomainGenerateView,
    DomainLaunchView,
    DomainRecordView,
    DomainsView,
    DomainView,
)
from api.views.email_address import EmailAddressView
from api.views.proxies import ProxiesView, ProxyView
from api.views.templates import (
    TemplateAttributesView,
    TemplateContentView,
    TemplatesView,
    TemplateView,
)
from api.views.users import (
    UserAdminStatusView,
    UserConfirmView,
    UserGroupsView,
    UsersView,
    UserView,
)
from settings import STATIC_GEN_URL, logger
from utils.decorators.auth import auth_admin_required, auth_required

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# register apps
url_prefix = "/api"

rules = [
    ("/generate-email-address/", EmailAddressView),
    ("/categories/", CategoriesView),
    ("/check/", CategoryCheckView),
    ("/proxies/", ProxiesView),
    ("/proxy/<proxy_id>/", ProxyView),
    ("/templates/", TemplatesView),
    ("/template/<template_id>/", TemplateView),
    ("/template/<template_id>/content/", TemplateContentView),
    ("/templates/attributes/", TemplateAttributesView),
    ("/domains/", DomainsView),
    ("/domain/<domain_id>/", DomainView),
    ("/domain/<domain_id>/categorize/", DomainCategorizeView),
    ("/domain/<domain_id>/check/", DomainCategoryCheckView),
    ("/domain/<domain_id>/content/", DomainContentView),
    ("/domain/<domain_id>/deployed/", DomainDeployedCheckView),
    ("/domain/<domain_id>/generate/", DomainGenerateView),
    ("/domain/<domain_id>/launch/", DomainLaunchView),
    ("/domain/<domain_id>/records/", DomainRecordView),
]

admin_rules = [
    ("/applications/", ApplicationsView),
    ("/application/<application_id>/", ApplicationView),
    ("/users/", UsersView),
    ("/user/<username>/", UserView),
    ("/user/<username>/confirm", UserConfirmView),
    ("/user/<username>/admin", UserAdminStatusView),
    ("/user/<username>/groups", UserGroupsView),
]

for rule in rules:
    url = f"{url_prefix}{rule[0]}"
    if not rule[1].decorators:
        rule[1].decorators = []
    rule[1].decorators.append(auth_required)
    app.add_url_rule(url, view_func=rule[1].as_view(url))

for rule in admin_rules:
    url = f"{url_prefix}{rule[0]}"
    if not rule[1].decorators:
        rule[1].decorators = []
    rule[1].decorators.append(auth_admin_required)
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
    golang_resp = requests.get(f"{STATIC_GEN_URL}/health/")
    return render_template(
        "index.html", endpoints=endpoints, golang_resp=golang_resp.text
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
