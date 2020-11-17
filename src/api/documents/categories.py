"""Category documents."""
# Standard Python Libraries
import datetime

# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db.base import Document, db


class Category(Document):
    """Document model for site categories."""

    def __init__(self, **kwargs):
        """Initialize arguments."""
        self.fields = ["name"]
        self.document = {k: kwargs.get(k) for k in self.fields}

    @staticmethod
    def get_all():
        """Get all categories."""
        return [x for x in db.categories.find()]

    @staticmethod
    def get_by_name(category_name):
        """Get category by name."""
        return db.categories.find_one({"name": category_name})
