"""Domain manager."""
# Standard Python Libraries
from datetime import date

# Third-Party Libraries
from apscheduler.schedulers.background import BackgroundScheduler
from flask import g, render_template, request
from flask.json import JSONEncoder
import requests  # type: ignore

# cisagov Libraries
from api.app import app
from api.config import EMAIL_SCHEDULE, STATIC_GEN_URL, logger
from api.manager import ApplicationManager, DomainManager, LogManager, TemplateManager
from api.tasks import email_categorization_updates
from api.views.about_views import AboutView
from api.views.application_views import (
    ApplicationBulkDomainView,
    ApplicationsView,
    ApplicationsViewNoAuth,
    ApplicationView,
)
from api.views.auth_views import (
    RefreshTokenView,
    RegisterView,
    ResetPasswordView,
    SignInView,
)
from api.views.category_views import (
    CategoriesView,
    CategorizationsView,
    CategorizationView,
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
from api.views.external_views import (
    ExternalDomainCategorizeView,
    ExternalDomainsView,
    ExternalDomainView,
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

# register apps
url_prefix = "/api"

rules = [
    ("/about/", AboutView),
    ("/applications/", ApplicationsView),
    ("/categories/", CategoriesView),
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
    ("/external-domains/", ExternalDomainsView),
    ("/external-domain/<external_id>/", ExternalDomainView),
    ("/external-domain/<external_id>/categorize/", ExternalDomainCategorizeView),
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
    ("/auth/register/", RegisterView),
    ("/auth/resetpassword/<username>/", ResetPasswordView),
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
    if not rule[1].decorators:  # type: ignore
        rule[1].decorators = []  # type: ignore
    rule[1].decorators.extend([auth_required])  # type: ignore
    app.add_url_rule(url, view_func=rule[1].as_view(url))  # type: ignore

for rule in login_rules:
    url = f"{url_prefix}{rule[0]}"
    app.add_url_rule(url, view_func=rule[1].as_view(url))  # type: ignore

for rule in admin_rules:
    url = f"{url_prefix}{rule[0]}"
    if not rule[1].decorators:  # type: ignore
        rule[1].decorators = []  # type: ignore
    rule[1].decorators.extend([auth_admin_required, auth_required])  # type: ignore
    app.add_url_rule(url, view_func=rule[1].as_view(url))  # type: ignore


# AP Scheduler
sched = BackgroundScheduler()
sched.add_job(email_categorization_updates, trigger=EMAIL_SCHEDULE)
sched.start()


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
    # each value in _rules_by_endpoint is a list with one element.
    # first index is pulled for quick access to the value's properties
    endpoints = {
        k: f"{v[0].methods}  {v[0].rule}"
        for k, v in app.url_map.__dict__["_rules_by_endpoint"].items()
        if k not in ["static", "api_map"]
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
        if data.get("username"):
            log_manager = LogManager()
            if data.get("args", {}).get("domain_id"):
                domain_manager = DomainManager()
                data["domain_name"] = domain_manager.get(
                    document_id=data["args"]["domain_id"], fields=["name"]
                )["name"]
            if data.get("args", {}).get("application_id"):
                application_manager = ApplicationManager()
                data["application_name"] = application_manager.get(
                    document_id=data["args"]["application_id"], fields=["name"]
                )["name"]
            if data.get("args", {}).get("template_id"):
                template_manager = TemplateManager()
                data["template_name"] = template_manager.get(
                    document_id=data["args"]["template_id"], fields=["name"]
                )["name"]
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
