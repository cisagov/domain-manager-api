"""Websites documents."""
# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db.doc import Document, db


class Website(Document):
    """
    Document model for websites.

    Note: DO NOT MODIFY. Website data is managed by AWS S3.
    """

    def __init__(self, **kwargs):
        """Initialize arguments."""
        self.fields = [
            "name",
            "url",
        ]
        self.document = {k: kwargs.get(k) for k in self.fields}

    @staticmethod
    def get_by_id(website_id):
        """Get domain by id."""
        return db.websites.find_one({"_id": ObjectId(website_id)})

    @staticmethod
    def get_all():
        """Get all available websites in s3."""
        return [x for x in db.websites.find()]
