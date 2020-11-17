"""Application Document."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from utils.db.base import Document
from utils.db.datatypes import StringType, DatetimeType


class Application(Document):
    """Application document model."""

    name: StringType
    requester_name: StringType
    created: DatetimeType

    def __init__(self, _id=None):
        """Initialize collection and indices."""
        self._id = _id
        self.collection = "applications"
        self.indexes = ["name"]

    def create(self, name):
        """Create a new application."""
        self.name = name
        self.requester_name = "Dev User"
        self.created = datetime.now()
        return super().create()
