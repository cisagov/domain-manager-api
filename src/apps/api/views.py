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


@api.route("/domains/", methods=["GET"])
def domain_list():
    """Get a list of domains."""
    domain_list = get_list(request.get_json(), "domain", DomainModel, validate_domain)
    return domains_schema.dump(domain_list)
