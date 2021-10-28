"""Category Views."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CategorizationManager, DomainManager
from api.schemas.categorization_schema import CategorizationSchema
from utils.categorization import CATEGORIES
from utils.validator import validate_data

categorization_manager = CategorizationManager()
domain_manager = DomainManager()


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

        domain = domain_manager.get(
            document_id=put_data["domain_id"], fields=["burned_date"]
        )

        if not domain.get("burned_date") and put_data["status"] == "burned":
            domain_manager.update(
                document_id=put_data["domain_id"],
                data={"burned_date": datetime.utcnow()},
            )

        return jsonify(
            categorization_manager.update(document_id=categorization_id, data=put_data)
        )
