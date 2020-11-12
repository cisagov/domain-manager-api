"""Database utilities."""
# Standard Python Libraries
import os
import json
from datetime import datetime
from dataclasses import dataclass
from bson.objectid import ObjectId

# Third-Party Libraries
from pymongo import MongoClient

if os.environ.get("MONGO_TYPE", "MONGO") == "DOCUMENTDB":
    CONN_STR = "mongodb://{}:{}@{}:{}/?ssl=true&ssl_ca_certs=/var/www/rds-combined-ca-bundle.pem&retryWrites=false".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
    )

else:
    CONN_STR = "mongodb://{}:{}@{}:{}/".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
    )

client = MongoClient(CONN_STR)

# Set database
db = client.domain_management


class Document:
    """Database Document structure."""

    def to_dict(self):
        """Return dictionary."""
        return self.__dict__

    def create(self):
        """Create a document."""
        self.requester_name = "Dev User"
        self.created = datetime.now()
        return self.get_collection().insert_one(self.to_dict())

    def all(self):
        """Get all documents."""
        return [document for document in self.get_collection().find()]

    def get(self, _id=None):
        """Get a single document."""
        if _id:
            response = self.get_collection().find_one({"_id": ObjectId(_id)})
        else:
            response = self.get_collection().find_one(self.to_dict())
        return response

    def delete(self, _id):
        """Delete a document by its id."""
        return self.get_collection().delete_one({"_id": ObjectId(_id)})
