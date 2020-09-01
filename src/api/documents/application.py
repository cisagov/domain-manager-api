"""Domain documents."""
# Standard Python Libraries
import datetime

# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db import Document, db


class Application(Document):
    """Document model for applications utilizing the domain manager."""

    def __init__(self, **kwargs):
        """Initialize arguments."""
        self.fields = ["name", "is_available", "requester_name", "requested_date"]
        self.document = {k: kwargs.get(k) for k in self.fields}

    @staticmethod
    def get_by_id(application_id):
        """Get application by id."""
        return db.applications.find_one({"_id": ObjectId(application_id)})

    @staticmethod
    def get_all():
        """Get all registered applications."""
        return [x for x in db.applications.find()]

    @staticmethod
    def create(name):
        """Create an application."""
        # make names unique
        if "applications" not in db.list_collection_names():
            db.applications.create_index("name", unique=True)

        post_data = {
            "name": name,
            "is_available": True,
            "requester_name": "dev_user",
            "requested_date": datetime.datetime.utcnow(),
        }
        return db.applications.insert_one(post_data)

    @staticmethod
    def update(application_id, **kwargs):
        """Update an existing post document."""
        update = dict()
        if "name" in kwargs:
            update["name"] = kwargs.get("name")

        if "is_available" in kwargs:
            update["is_available"] = kwargs.get("is_available")

        db.applications.find_one_and_update(
            {"_id": ObjectId(application_id)}, {"$set": update}
        )

    @staticmethod
    def delete(application_id):
        """Delete application by id."""
        return db.applications.delete_one({"_id": ObjectId(application_id)})
