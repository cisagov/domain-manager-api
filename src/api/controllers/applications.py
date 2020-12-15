"""Applications controller."""
# cisagov Libraries
from api.schemas.application_schema import ApplicationSchema
from models.application import Application


def applications_manager(request, application_id=None):
    """Manage applications."""
    if not application_id:
        application = Application()
        if request.method == "POST":
            name = request.json.get("name")
            application.create(name=name)
            response = {"message": f"Application with name {name} has been created."}
        else:
            applications_schema = ApplicationSchema(many=True)
            response = applications_schema.dump(application.all())
        return response

    application = Application(_id=application_id)
    if request.method == "DELETE":
        application.delete()
        response = {"message": "Application has been deleted."}
    elif request.method == "PUT":
        application.name = request.json.get("name")
        application.update()
        response = {"message": "Application has been updated."}
    else:
        application_schema = ApplicationSchema()
        response = application_schema.dump(application.get())

    return response
