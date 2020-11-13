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

    def asdict(self):
        """Return dictionary."""
        response = {
            key: value for key, value in self.__dict__.items() if value is not None
        }
        response.pop("_id", None)
        return response

    def create(self):
        """Create a document."""
        return self.get_collection().insert_one(self.asdict())

    def all(self):
        """Get all documents."""
        return [document for document in self.get_collection().find()]

    def get(self):
        """Get a single document."""
        if self._id:
            response = self.get_collection().find_one({"_id": ObjectId(self._id)})
        else:
            response = self.get_collection().find_one(self.asdict())
        return response

    def update(self):
        """Update an existing document."""
        if self._id:
            return self.get_collection().find_one_and_update(
                {"_id": ObjectId(self._id)}, {"$set": self.asdict()}
            )

    def delete(self):
        """Delete a document by its id."""
        return self.get_collection().delete_one({"_id": ObjectId(self._id)})
