"""Hosted zone views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from utils.aws.dns_record_handler import delete_hosted_zone, generate_hosted_zone


class HostedZonesView(MethodView):
    """HostedZonesView."""

    def delete(self):
        """Delete hosted zone."""
        response = {}
        for domain in request.json.get("domains"):
            response[domain] = delete_hosted_zone(domain)
        return jsonify(response)

    def post(self):
        """Create hosted zone."""
        response = {}
        for domain in request.json.get("domains"):
            response[domain] = generate_hosted_zone(domain)
        return jsonify(response)
