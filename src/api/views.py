"""API routes."""
# Third-Party Libraries
from utils.db_utils import db

# cisagov Libraries
from api.documents.domain_documents import Domain
from api.documents.website_documents import Website
from api.schemas.domain_schema import DomainSchema
from api.schemas.website_schema import WebsiteSchema
from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__, url_prefix="/api")

# Schemas
domains_schema = DomainSchema(many=True)
domain_schema = DomainSchema()
websites_schema = WebsiteSchema(many=True)
website_schema = WebsiteSchema()


@api.route("/domains/", methods=["GET"])
def domain_list():
    """Get a list of domains."""
    response = domains_schema.dump(Domain.get_all())
    return jsonify(response), 200


@api.route("/domain/<domain_id>/")
def get_domain(domain_id):
    """Get a domain by its id."""
    response = domain_schema.dump(Domain.get_by_id(domain_id))
    return jsonify(response), 200


@api.route("/websites/", methods=["GET"])
def website_list():
    """Get a list of websites."""
    response = websites_schema.dump(Website.get_all())
    return jsonify(response), 200


@api.route("/website/<website_id>/")
def get_website(website_id):
    """Get a website's data by its id."""
    response = website_schema.dump(Website.get_by_id(website_id))
    return jsonify(response), 200
