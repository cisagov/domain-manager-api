"""Tag documents."""
# Standard Python Libraries
import datetime

# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db.doc import Document, db


class Tag(Document):
    """Document model for domain tags."""

    def __init__(self, **kwargs):
        """Initialize arguments."""
        self.fields = ["name"]
        self.document = {k: kwargs.get(k) for k in self.fields}

    @staticmethod
    def get_by_id(tag_id):
        """Get tag by id."""
        return db.tags.find_one({"_id": ObjectId(tag_id)})

    @staticmethod
    def get_all():
        """Get all tags."""
        return [x for x in db.tags.find()]

    @staticmethod
    def create(name):
        """Create a domain tag."""
        # make names unique
        if "tags" not in db.list_collection_names():
            db.tags.create_index("name", unique=True)

        post_data = {
            "name": name,
        }
        return db.tags.insert_one(post_data)

    @staticmethod
    def update(tag_id, **kwargs):
        """Update an existing tag document."""
        update = dict()
        if "name" in kwargs:
            update["name"] = kwargs.get("name")

        db.tags.find_one_and_update({"_id": ObjectId(tag_id)}, {"$set": update})

    @staticmethod
    def delete(tag_id):
        """Delete tag by id."""
        return db.tags.delete_one({"_id": ObjectId(tag_id)})
