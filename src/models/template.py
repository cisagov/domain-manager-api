"""Template document."""
# Standard Python Libraries
from datetime import datetime

# cisagov Libraries
from utils.db.base import Document
from utils.db.datatypes import DatetimeType, StringType


class Template(Document):
    """Template document model."""

    name: StringType
    url: StringType
    created: DatetimeType

    def __init__(self, _id=None):
        """Initialize collection and indices."""
        self._id = _id
        self.collection = "templates"
        self.indexes = ["name"]

    def create(self, name):
        """Create a new template."""
        self.name = name
        self.created = datetime.now()
        return super().create()
