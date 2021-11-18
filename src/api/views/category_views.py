"""Category Views."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CategorizationManager, DomainManager, ExternalManager
from api.schemas.categorization_schema import CategorizationSchema
from utils.categorization import CATEGORIES
from utils.validator import validate_data

categorization_manager = CategorizationManager()
domain_manager = DomainManager()
external_manager = ExternalManager()


class CategoriesView(MethodView):
    """CategoriesView."""

    def get(self):
        """Get all categories."""
        return jsonify(CATEGORIES)


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

        if not domain:
            external_domain = external_manager.get(
                document_id=put_data["domain_id"], fields=["burned_date"]
            )

            if (
                not external_domain.get("burned_date")
                and put_data["status"] == "burned"
            ):
                external_manager.update(
                    document_id=put_data["domain_id"],
                    data={"burned_date": datetime.utcnow()},
                )
        else:
            if not domain.get("burned_date") and put_data["status"] == "burned":
                domain_manager.update(
                    document_id=put_data["domain_id"],
                    data={"burned_date": datetime.utcnow()},
                )

        return jsonify(
            categorization_manager.update(document_id=categorization_id, data=put_data)
        )
