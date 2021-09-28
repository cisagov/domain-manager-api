"""Category Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CategorizationManager
from api.schemas.categorization_schema import CategorizationSchema
from utils.categorization import CATEGORIES
from utils.validator import validate_data

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
        status = request.args.get("status").split(",")
        if not status:
            return jsonify({"message": "Please specify a status"}), 406

        return (
            jsonify(categorization_manager.all(params={"status": {"$in": status}})),
            200,
        )


class CategorizationView(MethodView):
    """CategorizationView."""

    def put(self, categorization_id):
        """Update categorization data."""
        put_data = validate_data(request.json, CategorizationSchema)
        return jsonify(
            categorization_manager.update(document_id=categorization_id, data=put_data)
        )
