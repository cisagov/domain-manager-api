"""API routes."""
# Third-Party Libraries
from api.documents.active_site_documents import ActiveSite
from api.documents.application_documents import Application
from api.documents.domain_documents import Domain
from api.documents.website_documents import Website
from api.schemas.active_site_schema import ActiveSiteSchema
from api.schemas.application_schema import ApplicationSchema
from api.schemas.domain_schema import DomainSchema
from api.schemas.website_schema import WebsiteSchema
from flask import Blueprint, jsonify, request
from utils.aws_utils import delete_dns, delete_site, launch_site, setup_dns
from utils.db_utils import db
from utils.decorator_utils import auth_required

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
    if request.method == "POST":
        post_data = request.json
        application = Application.create(post_data.get("name"))
        response = {
            "message": f"Application with id {application.inserted_id} has been created."
        }
    else:
        applications_schema = ApplicationSchema(many=True)
        response = applications_schema.dump(Application.get_all())
    return jsonify(response), 200


@api.route("/application/<application_id>/", methods=["GET", "DELETE", "PUT"])
@auth_required
def get_application(application_id):
    """Get an application by its id. Update application data. Delete an application by its id."""
    if request.method == "DELETE":
        Application.delete(application_id)
        response = {"message": "Application has been deleted."}
    elif request.method == "PUT":
        put_data = request.json
        Application.update(application_id, put_data.get("name"))
        response = {"message": "Application has been updated."}
    else:
        application_schema = ApplicationSchema()
        response = application_schema.dump(Application.get_by_id(application_id))
    return jsonify(response), 200


@api.route("/active-sites/", methods=["GET", "POST"])
@auth_required
def active_site_list():
    """Get a list of active sites. Create a new active site."""
    if request.method == "POST":
        post_data = request.json
        website = Website.get_by_id(post_data.get("website_id"))
        domain = Domain.get_by_id(post_data.get("domain_id"))
        # launch s3 bucket and set dns
        live_site = launch_site(website, domain)
        # save to database
        active_site = ActiveSite.create(
            s3_url=live_site,
            domain_id=post_data.get("domain_id"),
            website_id=post_data.get("website_id"),
            application_id=post_data.get("application_id"),
        )
        response = {
            "message": f"Active site with id {active_site.inserted_id} has been launched. Visit: http://{live_site}"
        }
    else:
        active_sites_schema = ActiveSiteSchema(many=True)
        response = active_sites_schema.dump(ActiveSite.get_all())
    return jsonify(response), 200


@api.route("/active-site/<active_site_id>/", methods=["GET", "DELETE", "PUT"])
@auth_required
def get_active_site(active_site_id):
    """Get an active site by its id. Update active site data. Delete an active site by its id."""
    if request.method == "DELETE":
        active_site = ActiveSite.get_by_id(active_site_id)
        domain = Domain.get_by_id(active_site.get("domain").get("_id"))
        # delete s3 bucket and remove dns from domain
        delete_site(domain)
        # delete from database
        ActiveSite.delete(active_site_id)
        response = {"message": "Active site is now inactive and deleted."}
    elif request.method == "PUT":
        put_data = request.json
        ActiveSite.update(
            active_site_id=active_site_id,
            application_id=put_data.get("application_id"),
        )
        response = {"message": "Active site has been updated."}
    else:
        active_site_schema = ActiveSiteSchema()
        response = active_site_schema.dump(ActiveSite.get_by_id(active_site_id))
    return jsonify(response), 200