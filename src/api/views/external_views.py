"""External Domain Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import ExternalManager
from utils.categorization.categorize import (
    delete_domain_proxies,
    get_domain_proxies,
    post_categorize_request,
    put_proxy_status,
)

external_manager = ExternalManager()


class ExternalDomainsView(MethodView):
    """External Domains View."""

    def get(self):
        """Get all external domains."""
        return jsonify(external_manager.all())


class ExternalDomainCategorizeView(MethodView):
    """External Domain Categorize View."""

    def get(self, external_id):
        """Get categories on domains."""
        resp, status_code = get_domain_proxies(external_id)
        return jsonify(resp), status_code

    def post(self, external_id):
        """Submit a Domain for Categorization."""
        category = request.json.get("category")
        email = request.json.get("email")

        if not category:
            return jsonify({"error": "Please specify a requested category."}), 406

        if not email:
            return (
                jsonify(
                    {"error": "Please specify an email address to submit to proxies."}
                ),
                406,
            )

        external_domain = external_manager.get(document_id=external_id)

        if external_domain.get("rejected_msg"):
            external_manager.update(
                document_id=external_id, data={"rejected_msg": None}
            )

        resp, status_code = post_categorize_request(
            domain_id=external_id,
            domain_name=external_domain["name"],
            requested_category=category,
        )

        return jsonify(resp), status_code

    def put(self, external_id):
        """Verify a domain has been categorized."""
        status = request.json.get("status")

        if not status:
            return jsonify({"error": "Please specify a proxy status"}), 406

        category = request.json.get("category")

        if not category:
            return jsonify({"error": "Please specify a category"}), 406

        resp, status_code = put_proxy_status(
            domain_id=external_id, status=status, category=category
        )

        return jsonify(resp), status_code

    def delete(self, external_id):
        """Delete proxies for a domain."""
        resp, status_code = delete_domain_proxies(external_id)
        external_manager.update(
            document_id=external_id, data={"rejected_msg": request.json.get("message")}
        )
        return jsonify(resp), status_code
