"""Category Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CategorizationManager
from utils.categorization import CATEGORIES

categorization_manager = CategorizationManager()


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

        return jsonify(categorization_manager.all(params={"status": status})), 200
