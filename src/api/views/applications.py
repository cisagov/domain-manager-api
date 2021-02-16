"""Application Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import ApplicationManager, DomainManager
from api.schemas.application_schema import ApplicationSchema
from utils.validator import validate_data

application_manager = ApplicationManager()
domain_manager = DomainManager()


class ApplicationsView(MethodView):
    """ApplicationsView."""

    def get(self):
        """Get all applications."""
        return jsonify(application_manager.all())

    def post(self):
        """Create an application."""
        data = validate_data(request.json, ApplicationSchema)
        return jsonify(application_manager.save(data))


class ApplicationView(MethodView):
    """ApplicationView."""

    def get(self, application_id):
        """Get application by id."""
        application = application_manager.get(document_id=application_id)
        return jsonify(application)

    def put(self, application_id):
        """Update application by id."""
        data = validate_data(request.json, ApplicationSchema)
        return jsonify(
            application_manager.update(document_id=application_id, data=data)
        )

    def delete(self, application_id):
        """Delete application by id."""
        application_domains = domain_manager.all(
            params={"application_id": {"$eq": application_id}}
        )
        if application_domains:
            return (
                jsonify(
                    {
                        "error": "Can not delete an application that has domains attached to it"
                    }
                ),
                400,
            )
        return jsonify(application_manager.delete(document_id=application_id))
