"""Domain tags controller."""
# Third-Party Libraries
from api.documents.tag import Tag
from api.schemas.tag_schema import TagSchema


def tags_manager(request, tag_id=None):
    """Manage tags."""
    if not tag_id:
        if request.method == "POST":
            post_data = request.json
            tag = Tag.create(post_data.get("name"))
            response = {"message": f"Tag with id {tag.inserted_id} has been created."}
        else:
            tags_schema = TagSchema(many=True)
            response = tags_schema.dump(Tag.get_all())
        return response

    if request.method == "DELETE":
        Tag.delete(tag_id)
        response = {"message": "Tag has been deleted."}
    elif request.method == "PUT":
        put_data = request.json
        Tag.update(tag_id=tag_id, name=put_data.get("name"))
        response = {"message": "Tag has been updated."}
    else:
        tag_schema = TagSchema()
        response = tag_schema.dump(Tag.get_by_id(tag_id))

    return response
