"""Application documents."""
# Standard Python Libraries
from datetime import datetime
from dataclasses import dataclass, field
from typing import Union

# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db import Document, db


@dataclass
class Application(Document):
    """Application model."""

    _id: Union[str, None] = field(default=None)
    name: Union[str, None] = field(default=None)
    requester_name: Union[str, None] = field(default=None)
    created: Union[datetime, None] = field(default=None)

    def create(self):
        """Create a new application."""
        # make names unique
        if "applications" not in db.list_collection_names():
            self.get_collection().create_index("name", unique=True)

        self.requester_name = "Dev User"
        self.created = datetime.now()
        return super().create()

    def get_collection(self):
        """Set collection name."""
        return db.applications
