"""Proxy Document."""
# Standard Python Libraries
from datetime import datetime
from typing import Union

# cisagov Libraries
from utils.db.base import Document
from utils.db.datatypes import BytesType, DatetimeType, ListType, StringType


class Proxy(Document):
    """Proxy document model."""

    _id: StringType
    name: StringType
    url: StringType
    script: BytesType
    categories: ListType
    created_by: StringType
    created: DatetimeType

    def __init__(self, _id=None):
        """Initialize collection and indicies."""
        self._id = _id
        self.collection = "proxies"
        self.indexes = ["name"]

    def create(self, name):
        """Create a new proxy."""
        self.name = name
        self.requester_name = "Dev User"
        self.created = datetime.now()
        return super().create()
