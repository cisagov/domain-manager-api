"""Category documents."""
# Standard Python Libraries
from datetime import datetime
from typing import Union

# Third-Party Libraries
from utils.db.doc import Document
from utils.db.types import string_type, dict_type


class Category(Document):
    """Category document model."""

    _id: string_type
    name: string_type
    proxies: dict_type

    def __init__(self, _id=None):
        """Initialize collection name."""
        self._id = _id
        self.collection = "categories"
        self.indexes = ["name"]
