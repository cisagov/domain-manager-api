"""API routes."""
# Third-Party Libraries
from api.documents.domain_documents import Domain
from api.documents.website_documents import Website
from api.schemas.domain_schema import DomainSchema
from api.schemas.website_schema import WebsiteSchema
from flask import Blueprint, jsonify, request
from utils.db_utils import db

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/domains/", methods=["GET"])
def domain_list():
    """Get a list of domains."""
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
    """Get a list of websites."""
    websites_schema = WebsiteSchema(many=True)
    response = websites_schema.dump(Website.get_all())
    return jsonify(response), 200


@api.route("/website/<website_id>/")
def get_website(website_id):
    """Get a website's data by its id."""
    website_schema = WebsiteSchema()
    response = website_schema.dump(Website.get_by_id(website_id))
    return jsonify(response), 200
