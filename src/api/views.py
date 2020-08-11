"""API routes."""
# Third-Party Libraries
from api.documents.application_documents import Application
from api.documents.domain_documents import Domain
from api.documents.website_documents import Website
from api.schemas.application_schema import ApplicationSchema
from api.schemas.domain_schema import DomainSchema
from api.schemas.website_schema import WebsiteSchema
from flask import Blueprint, jsonify, request
from utils.db_utils import db

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/domains/", methods=["GET"])
def domain_list():
    """Get a list of domains managed by namecheap."""
    domains_schema = DomainSchema(many=True)
    response = domains_schema.dump(Domain.get_all())
    return jsonify(response), 200


@api.route("/domain/<domain_id>/")
def get_domain(domain_id):
    """Get a domain by its id."""
    domain_schema = DomainSchema()
    response = domain_schema.dump(Domain.get_by_id(domain_id))
    return jsonify(response), 200


@api.route("/websites/", methods=["GET"])
def website_list():
    """Get a list of websites managed by aws s3 bucket."""
    websites_schema = WebsiteSchema(many=True)
    response = websites_schema.dump(Website.get_all())
    return jsonify(response), 200


@api.route("/website/<website_id>/")
def get_website(website_id):
    """Get a website's data by its id."""
    website_schema = WebsiteSchema()
    response = website_schema.dump(Website.get_by_id(website_id))
    return jsonify(response), 200


@api.route("/applications/", methods=["GET", "POST"])
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


@api.route("/application/<application_id>/", methods=["GET", "DELETE"])
def get_application(application_id):
    """Get an application by its id. Delete an application by its id."""
    if request.method == "DELETE":
        Application.delete(application_id)
        response = {"message": "Application has been deleted."}
    else:
        application_schema = ApplicationSchema()
        response = application_schema.dump(Application.get_by_id(application_id))
    return jsonify(response), 200
