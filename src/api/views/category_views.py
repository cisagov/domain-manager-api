"""Category Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from utils.categorization import CATEGORIES


class CategoriesView(MethodView):
    """CategoriesView."""

    def get(self):
        """Get all categories."""
        return jsonify(CATEGORIES)


class ExternalCategoriesView(MethodView):
    """External Categories View."""

    def get(self, domain_name):
        """Check categories for external domains."""
        return jsonify({"message": "success"}), 200

    def post(self, domain_name):
        """Categorize an external domain."""
        return jsonify(request.json.get("category", ""), domain_name)


class CategorizationsView(MethodView):
    """CategorizationsView."""

    def get(self):
        """Get all domain categorizations."""
        status = request.args.get("status")
        if not status:
            return jsonify({"message": "Please specify a status"}), 406

        status = request.args.get("status")
        return jsonify({"message": f"success: {status}"}), 200
