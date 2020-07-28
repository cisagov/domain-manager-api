from flask import Blueprint, jsonify, request

from apps.api.models import DomainModel, validate_domain
from apps.api.serializers import DomainSerializer
from apps.database.utils import (
    get_list,
    get_single,
    save_single,
    update_single,
    delete_single,
)

api = Blueprint("api", __name__, url_prefix="/api")

# Schemas
domains_schema = DomainSerializer(many=True)
domain_schema = DomainSerializer()


@api.route("/domains/", methods=["GET", "POST"])
def domain_list():
    """
    Get a list of domains.
    Create a new domain object.
    """
    post_data = request.get_json()
    if request.method == "POST":

        domain_filter = {
            "name": post_data.get("name"),
        }
        existing_domain = get_list(
            domain_filter, "domain", DomainModel, validate_domain
        )
        if existing_domain:
            return jsonify({"message": "A domain with this name already exists."}), 202

        response = save_single(post_data, "domain", DomainModel, validate_domain)
    else:
        response = domains_schema.dump(
            get_list(post_data, "domain", DomainModel, validate_domain)
        )

    return jsonify(response), 200
