"""Category Document."""
# Standard Python Libraries
from datetime import datetime
from typing import Union

# Third-Party Libraries
from utils.db.base import Document
from utils.db.datatypes import StringType, DictType


class Category(Document):
    """Category document model."""

    _id: StringType
    name: StringType
    proxies: DictType

    def __init__(self, _id=None):
        """Initialize collection and indices."""
        self._id = _id
        self.collection = "categories"
        self.indexes = ["name"]
