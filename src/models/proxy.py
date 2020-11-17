"""Proxy Document."""
# Standard Python Libraries
from datetime import datetime
from typing import Union

# Third-Party Libraries
from utils.db.base import Document
from utils.db.datatypes import Bytes, Datetime, Dicttype, Listtype, Stringtype


class Proxy(Document):
    """Proxy document model."""

    _id: Stringtype
    name: Stringtype
    url: Stringtype
    script: Bytes
    categories: Listtype
    created_by: Stringtype
    created: Datetime

    def __init__(self, _id=None):
        """Initialize collection and indicies."""
        self._id = _id
        self.collection = "proxies"
        self.indexes = ["name"]

    def create(self, name):
        """Create a new application."""
        self.name = name
        self.requester_name = "Dev User"
        self.created = datetime.now()
        return super().create()
