"""Domain documents."""
# Standard Python Libraries
import datetime

# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db_utils import Document, db


class Application(Document):
    """Document model for applications utilizing the domain manager."""

    def __init__(self, **kwargs):
        """Initialize arguments."""
        self.fields = ["name", "requester_name", "requested_date"]
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
            "requester_name": "dev_user",
            "requested_date": datetime.datetime.utcnow(),
        }
        return db.applications.insert_one(post_data)

    @staticmethod
    def delete(application_id):
        """Delete application by id."""
        return db.applications.delete_one({"_id": ObjectId(application_id)})
