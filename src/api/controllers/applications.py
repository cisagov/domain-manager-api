"""Applications controller."""
# Third-Party Libraries
from api.documents.application import Application
from api.schemas.application_schema import ApplicationSchema


def applications_manager(request, application_id=None):
    """Manage applications."""
    if not application_id:
        if request.method == "POST":
            post_data = request.json
            application = Application.create(post_data.get("name"))
            response = {
                "message": f"Application with id {application.inserted_id} has been created."
            }
        else:
            applications_schema = ApplicationSchema(many=True)
            response = applications_schema.dump(Application.get_all())
        return response

    if request.method == "DELETE":
        Application.delete(application_id)
        response = {"message": "Application has been deleted."}
    elif request.method == "PUT":
        put_data = request.json
        Application.update(application_id, put_data.get("name"))
        response = {"message": "Application has been updated."}
    else:
        application_schema = ApplicationSchema()
        response = application_schema.dump(Application.get_by_id(application_id))

    return response
