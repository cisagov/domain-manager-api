"""Proxy documents."""
# Standard Python Libraries
import datetime

# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db.doc import Document, db


class Proxy(Document):
    """Document model for managing proxies."""

    def __init__(self, **kwargs):
        """Initialize arguments."""
        self.fields = [
            "name",
            "url",
            "script",
            "categories",
            "created_by",
            "created_date",
        ]
        self.document = {k: kwargs.get(k) for k in self.fields}

    @staticmethod
    def get_by_id(proxy_id):
        """Get proxy by id."""
        return db.proxies.find_one({"_id": ObjectId(proxy_id)})

    @staticmethod
    def get_by_name(proxy_name):
        """Get proxy by name."""
        return db.proxies.find_one({"name": proxy_name})

    @staticmethod
    def get_all():
        """Get all proxies."""
        return [x for x in db.proxies.find()]

    @staticmethod
    def create(name, url, script, categories):
        """Create a proxy."""
        # make names unique
        if "proxies" not in db.list_collection_names():
            db.proxies.create_index("name", unique=True)

        post_data = {
            "name": name,
            "url": url,
            "script": script,
            "categories": categories,
            "created_by": "dev_user",
            "created_date": datetime.datetime.utcnow(),
        }
        return db.proxies.insert_one(post_data)

    @staticmethod
    def update(proxy_id, **kwargs):
        """Update an existing proxy."""
        update = dict()
        if "name" in kwargs:
            update["name"] = kwargs.get("name")

        if "url" in kwargs:
            update["url"] = kwargs.get("url")

        if "script" in kwargs:
            update["script"] = kwargs.get("script")

        db.proxies.find_one_and_update({"_id": ObjectId(proxy_id)}, {"$set": update})

    @staticmethod
    def delete(proxy_id):
        """Delete proxy by id."""
        return db.proxies.delete_one({"_id": ObjectId(proxy_id)})
