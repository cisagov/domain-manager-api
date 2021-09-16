"""Domain manager."""
# Standard Python Libraries
from datetime import date

# Third-Party Libraries
from flask import Flask, g, render_template, request
from flask.json import JSONEncoder
from flask_cors import CORS
import requests

# cisagov Libraries
from api.config import STATIC_GEN_URL, logger
from api.manager import LogManager
from api.views.about_views import AboutView
from api.views.application_views import (
    ApplicationBulkDomainView,
    ApplicationsView,
    ApplicationsViewNoAuth,
    ApplicationView,
)
from api.views.auth_views import (
    ConfirmSignUpView,
    RefreshTokenView,
    RegisterView,
    ResetPasswordView,
    SignInView,
)
from api.views.category_views import (
    CategoriesView,
    CategorizationsView,
    CategorizationView,
    ExternalCategoriesView,
)
from api.views.domain_views import (
    DomainApprovalView,
    DomainCategorizeView,
    DomainContentView,
    DomainDeployedCheckView,
    DomainEmailsView,
    DomainEmailView,
    DomainGenerateView,
    DomainLaunchView,
    DomainReceiveEmailsView,
    DomainRecordView,
    DomainsView,
    DomainView,
)
from api.views.proxy_views import ProxiesView, ProxyView
from api.views.settings_views import SettingsView
from api.views.template_views import (
    TemplateApprovalView,
    TemplateAttributesView,
    TemplateContentView,
    TemplatesView,
    TemplateView,
)
from api.views.user_views import (
    UserAdminStatusView,
    UserAPIKeyView,
    UserConfirmView,
    UserGroupsView,
    UsersView,
    UserView,
)
from utils.decorators.auth import auth_admin_required, auth_required

app = Flask(__name__, template_folder="templates")
app.url_map.strict_slashes = False
CORS(app)

# register apps
url_prefix = "/api"

rules = [
    ("/about/", AboutView),
    ("/applications/", ApplicationsView),
    ("/categories/", CategoriesView),
    ("/categories/<domain_name>/external/", ExternalCategoriesView),
    ("/categorization/<categorization_id>/", CategorizationView),
    ("/categorizations/", CategorizationsView),
    ("/domains/", DomainsView),
    ("/domain/<domain_id>/", DomainView),
    ("/domain/<domain_id>/categorize/", DomainCategorizeView),
    ("/domain/<domain_id>/content/", DomainContentView),
    ("/domain/<domain_id>/deployed/", DomainDeployedCheckView),
    ("/domain/<domain_id>/emails/", DomainEmailsView),
    ("/domain/<domain_id>/generate/", DomainGenerateView),
    ("/domain/<domain_id>/launch/", DomainLaunchView),
    ("/domain/<domain_id>/records/", DomainRecordView),
    ("/domain/<domain_id>/receive-emails/", DomainReceiveEmailsView),
    ("/email/<email_id>/", DomainEmailView),
    ("/proxies/", ProxiesView),
    ("/proxy/<proxy_name>/", ProxyView),
    ("/templates/", TemplatesView),
    ("/template/<template_id>/", TemplateView),
    ("/template/<template_id>/content/", TemplateContentView),
    ("/templates/attributes/", TemplateAttributesView),
    ("/user/<username>/", UserView),
    ("/user/<username>/api", UserAPIKeyView),
    ("/settings/", SettingsView),
]

login_rules = [
    ("/auth/applications/", ApplicationsViewNoAuth),
    ("/auth/confirm/", ConfirmSignUpView),
    ("/auth/register/", RegisterView),
    ("/auth/resetpassword/", ResetPasswordView),
    ("/auth/signin/", SignInView),
    ("/auth/refreshtoken/", RefreshTokenView),
]

admin_rules = [
    ("/application/<application_id>/", ApplicationView),
    ("/application/<application_id>/domains/", ApplicationBulkDomainView),
    ("/domain/<domain_id>/approve/", DomainApprovalView),
    ("/template/<template_id>/approve/", TemplateApprovalView),
    ("/users/", UsersView),
    ("/user/<username>/confirm", UserConfirmView),
    ("/user/<username>/admin", UserAdminStatusView),
    ("/user/<username>/groups", UserGroupsView),
]

for rule in rules:
    url = f"{url_prefix}{rule[0]}"
    if not rule[1].decorators:
        rule[1].decorators = []
    rule[1].decorators.extend([auth_required])
    app.add_url_rule(url, view_func=rule[1].as_view(url))

for rule in login_rules:
    url = f"{url_prefix}{rule[0]}"
    app.add_url_rule(url, view_func=rule[1].as_view(url))

for rule in admin_rules:
    url = f"{url_prefix}{rule[0]}"
    if not rule[1].decorators:
        rule[1].decorators = []
    rule[1].decorators.extend([auth_admin_required, auth_required])
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


def get_request_data():
    """Get request data for logging."""
    data = {
        "username": g.get("username"),
        "is_admin": g.get("is_admin", False),
        "path": request.path,
        "method": request.method,
    }
    if request.view_args:
        data["args"] = request.view_args

    methods = ["POST", "PUT"]
    if (
        request.method in methods
        and "auth" not in request.path
        and "user" not in request.path
    ):
        data["json"] = request.json
    return data


@app.after_request
def log_request(response):
    """Log Request."""
    if request.method != "OPTIONS":
        data = get_request_data()
        data["status_code"] = response.status_code
        logger.info(data)
        if data.get("username"):
            log_manager = LogManager()
            log_manager.save(data)
    return response


@app.teardown_request
def log_request_error(error=None):
    """Log Request Error."""
    if error:
        data = get_request_data()
        data["status_code"] = 500
        data["error"] = str(error)
        logger.info(data)
        if data.get("username"):
            log_manager = LogManager()
            log_manager.save(data)


if __name__ == "__main__":
    app.run()
