"""Applications controller."""
# Third-Party Libraries
from models.application import Application
from api.schemas.application_schema import ApplicationSchema


def applications_manager(request, application_id=None):
    """Manage applications."""
    if not application_id:
        application = None
        if request.method == "POST":
            post_data = request.json.get("name")
            application = Application(name=post_data)
            application.create()
            response = {
                "message": f"Application with name {post_data} has been created."
            }
        else:
            applications_schema = ApplicationSchema(many=True)
            response = applications_schema.dump(Application().all())
        return response

    application = Application(_id=application_id)
    if request.method == "DELETE":
        application.delete()
        response = {"message": "Application has been deleted."}
    elif request.method == "PUT":
        put_data = request.json.get("name")
        application.name = put_data
        application.update()
        response = {"message": "Application has been updated."}
    else:
        application_schema = ApplicationSchema()
        response = application_schema.dump(application.get())

    return response
