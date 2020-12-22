"""API routes."""
# Standard Python Libraries
import io

# Third-Party Libraries
from flask import Blueprint, jsonify, request, send_file

# cisagov Libraries
from api.controllers.applications import applications_manager
from api.controllers.categorization import categories_manager, categorization_manager
from api.controllers.check import check_categories_manager
from api.controllers.email_address import email_address_manager
from api.controllers.hosted_zones import hosted_zones_manager
from api.controllers.proxies import proxy_manager
from api.controllers.templates import template_manager
from api.controllers.websites import generate_website_manager, website_manager
from utils.decorators.auth import auth_required

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/applications/", methods=["GET", "POST"])
@auth_required
def application_list():
    """Get a list of applications. Create a new application."""
    return jsonify(applications_manager(request)), 200


@api.route("/application/<application_id>/", methods=["GET", "DELETE", "PUT"])
@auth_required
def get_application(application_id):
    """
    Manage application by its id.

    Update application data. Delete an application by its id.
    """
    return jsonify(applications_manager(request, application_id=application_id)), 200


@api.route("/categories/", methods=["GET"])
@auth_required
def get_categories():
    """Check all categories."""
    resp = categories_manager()
    return jsonify(resp)


@api.route("/categorize/<website_id>/", methods=["GET"])
@auth_required
def categorize_domain(website_id):
    """Categorize an active site by using available proxies."""
    resp = categorization_manager(
        website_id=website_id, category=request.args.get("category")
    )
    return jsonify(resp)


@api.route("/check/", methods=["GET"])
@auth_required
def check_domain():
    """Check domain categorization."""
    resp = check_categories_manager(request.args.get("domain"))
    return jsonify(resp)


@api.route("/generate-dns/", methods=["POST", "DELETE"])
@auth_required
def generate_dns_record_handler():
    """Generate DNS record handlers in AWS Route53."""
    resp = hosted_zones_manager(request)
    return jsonify(resp)


@api.route("/generate-email-address/")
@auth_required
def generate_email_address():
    """Generate an email address using AWS SES."""
    resp = email_address_manager(request.args.get("domain"))
    return jsonify(resp)


@api.route("/proxies/", methods=["GET", "POST"])
@auth_required
def proxy_list():
    """Get a list of proxies. Create a new proxy."""
    return jsonify(proxy_manager(request)), 200


@api.route("/proxy/<proxy_id>/", methods=["GET", "DELETE", "PUT"])
@auth_required
def get_proxy(proxy_id):
    """
    Manage proxy by its id.

    Update proxy data. Delete a proxy by its id.
    """
    return jsonify(proxy_manager(request, proxy_id=proxy_id)), 200


@api.route("/templates/", methods=["GET", "POST"])
@auth_required
def templates_list():
    """Get a list of templates."""
    resp = template_manager()
    return jsonify(resp)


@api.route("/template/<template_id>/", methods=["GET"])
@auth_required
def template(template_id):
    """Download template zipfile."""
    resp, category = template_manager(template_id=template_id)

    # Create buffer
    buffer = io.BytesIO()
    buffer.write(resp)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        attachment_filename=f"{category}.zip",
        mimetype="application/zip",
    )


@api.route("/websites/", methods=["GET"])
@auth_required
def website_list():
    """Get a list of websites."""
    return jsonify(website_manager(request)), 200


@api.route("/website/<website_id>/", methods=["GET", "PUT"])
@auth_required
def website(website_id):
    """Manage a website by its id."""
    resp, domain = website_manager(request, website_id=website_id)
    if request.method == "GET":
        # Create buffer
        buffer = io.BytesIO()
        buffer.write(resp)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            attachment_filename=f"{domain}.zip",
            mimetype="application/zip",
        )

    return jsonify(resp), 200


@api.route("website/<website_id>/generate/", methods=["POST"])
@auth_required
def generate_website(website_id):
    """Generate website files from a template."""
    category = request.args.get("category")
    resp = generate_website_manager(request, website_id, category)
    return jsonify(resp)
