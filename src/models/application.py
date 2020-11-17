"""Application documents."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from utils.db.doc import Document
from utils.db.types import string_type, datetime_type


class Application(Document):
    """Application document model."""

    name: string_type
    requester_name: string_type
    created: datetime_type

    def __init__(self, _id=None):
        """Initialize collection name."""
        self._id = _id
        self.collection = "applications"
        self.indexes = ["name"]

    def create(self, name):
        """Create a new application."""
        self.name = name
        self.requester_name = "Dev User"
        self.created = datetime.now()
        return super().create()
