"""Application documents."""
# Standard Python Libraries
from datetime import datetime
from dataclasses import dataclass
from typing import Union

# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db import Document, db


@dataclass
class Application(Document):
    """Application model."""

    _id: Union[str, None] = None
    name: Union[str, None] = None
    requester_name: Union[str, None] = None
    created: Union[datetime, None] = None

    def create(self, name):
        """Create a new application."""
        # make names unique if it does not already exist
        self.get_collection().create_index("name", unique=True)

        self.name = name
        self.requester_name = "Dev User"
        self.created = datetime.now()
        return super().create()

    def update(self, name):
        """Upate an existing application."""
        self.name = name
        return super().update()

    def get_collection(self):
        """Set collection name."""
        return db.applications
