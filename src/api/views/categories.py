"""Category Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CategoryManager
from utils.categorization import (
    bluecoat,
    fortiguard,
    ibmxforce,
    trustedsource,
    websense,
)

category_manager = CategoryManager()


class CategoriesView(MethodView):
    """CategoriesView."""

    def get(self):
        """Get all categories."""
        return jsonify(category_manager.all())


class CategoryCheckView(MethodView):
    """CategoryCheckView."""

    def get(self):
        """Check category for a domain."""
        domain = request.args.get("domain")
        return jsonify(
            {
                "Trusted Source": trustedsource.check_category(domain),
                "Bluecoat": bluecoat.check_category(domain),
                # "Cisco Talos": ciscotalos.check_category(domain),
                "IBM X-Force": ibmxforce.check_category(domain),
                "Fortiguard": fortiguard.check_category(domain),
                "Websense": websense.check_category(domain),
            }
        )
