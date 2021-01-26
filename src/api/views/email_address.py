"""Email Views."""
# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView

# cisagov Libraries
from api.manager import DomainManager
from utils.aws.ses import create_email_address

domain_manager = DomainManager()


class EmailAddressView(MethodView):
    """EmailAddressView."""

    def get(self, domain_name):
        """Generate an email address using AWS SES."""
        domain = domain_manager.get(filter_data={"name": domain_name})
        if domain.get("is_email_active"):
            return {"error": f"Email address is already active for {domain_name}"}

        email_response = create_email_address(domain_name)

        domain_manager.update(document_id=domain["_id"], data={"is_email_active": True})

        return jsonify(
            {
                "message": f"Email records for {domain_name} has been created.",
                "status_code": email_response["ResponseMetadata"].get("HTTPStatusCode"),
            }
        )
