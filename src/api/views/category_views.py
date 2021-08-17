"""Category Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from utils.categorization import CATEGORIES
from utils.categorization.categorize import categorize


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
        return jsonify(categorize(request.json.get("category", ""), domain_name))
