"""API routes."""
# Third-Party Libraries
from api.controllers.active_sites import active_site_manager
from api.controllers.applications import applications_manager
from api.controllers.categorization import categorization_manager
from api.documents.domain import Domain
from api.documents.website import Website
from api.schemas.domain_schema import DomainSchema
from api.schemas.website_schema import WebsiteSchema
from flask import Blueprint, jsonify, request
from utils.decorators.auth import auth_required

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/domains/", methods=["GET"])
@auth_required
def domain_list():
    """Get a list of domains managed by route53."""
    domains_schema = DomainSchema(many=True)
    response = domains_schema.dump(Domain.get_all())
    return jsonify(response), 200


@api.route("/domain/<domain_id>/")
@auth_required
def get_domain(domain_id):
    """Get a domain by its id."""
    domain_schema = DomainSchema()
    response = domain_schema.dump(Domain.get_by_id(domain_id))
    return jsonify(response), 200


@api.route("/websites/", methods=["GET"])
@auth_required
def website_list():
    """Get a list of websites managed by aws s3 bucket."""
    websites_schema = WebsiteSchema(many=True)
    response = websites_schema.dump(Website.get_all())
    return jsonify(response), 200


@api.route("/website/<website_id>/")
@auth_required
def get_website(website_id):
    """Get a website's data by its id."""
    website_schema = WebsiteSchema()
    response = website_schema.dump(Website.get_by_id(website_id))
    return jsonify(response), 200


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


@api.route("/live-sites/", methods=["GET", "POST"])
@auth_required
def active_site_list():
    """Get a list of active sites. Create a new active site."""
    return jsonify(active_site_manager(request)), 200


@api.route("/live-site/<live_site_id>/", methods=["GET", "DELETE", "PUT"])
@auth_required
def get_active_site(live_site_id):
    """
    Manage an active site by its id.

    Update active site data. Delete an active site by its id.
    """
    return jsonify(active_site_manager(request, live_site_id=live_site_id)), 200


@api.route("/categorize/<live_site_id>/", methods=["GET"])
@auth_required
def categorize_domain(live_site_id):
    """Categorize an active site by using available proxies."""
    domain = categorization_manager(live_site_id=live_site_id)
    return jsonify({"message": f"{domain} has been categorized"})
