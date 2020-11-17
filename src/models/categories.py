"""Category Document."""
# Standard Python Libraries
from datetime import datetime
from typing import Union

# Third-Party Libraries
from utils.db.base import Document
from utils.db.datatypes import Stringtype, Dicttype


class Category(Document):
    """Category document model."""

    _id: Stringtype
    name: Stringtype
    proxies: Dicttype

    def __init__(self, _id=None):
        """Initialize collection and indices."""
        self._id = _id
        self.collection = "categories"
        self.indexes = ["name"]
