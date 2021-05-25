"""Application Views."""
# Standard Python Libraries
from http import HTTPStatus

# Third-Party Libraries
from flask import abort, g, jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import ApplicationManager, DomainManager
from api.schemas.application_schema import ApplicationSchema
from utils.users import get_users_group_ids
from utils.validator import validate_data

application_manager = ApplicationManager()
domain_manager = DomainManager()


class ApplicationsView(MethodView):
    """ApplicationsView."""

    def get(self):
        """Get all applications."""
        params = dict(request.args)
        if g.is_admin:
            return jsonify(application_manager.all(params=params))
        else:
            groups = get_users_group_ids()
            params.update({"_id": {"$in": groups}})
            resp = application_manager.all(params=params)
            return jsonify(resp)

    def post(self):
        """Create an application."""
        if not g.is_admin:
            abort(HTTPStatus.FORBIDDEN.value)
        data = validate_data(request.json, ApplicationSchema)
        return jsonify(application_manager.save(data))


class ApplicationsViewNoAuth(MethodView):
    """ApplicationsView for retrieving applications on the user register page without authorization."""

    def get(self):
        """Get base of all applications for the user register page."""
        return jsonify(application_manager.all(fields=["name", "_id"]))


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
