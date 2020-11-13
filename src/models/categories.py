"""Category documents."""
# Standard Python Libraries
from datetime import datetime
from typing import Union

# Third-Party Libraries
from utils.db import Document


class Category(Document):
    """Category document model."""

    _id: Union[str, None] = None
    name: Union[str, None] = None

    def __init__(self, _id=None):
        """Initialize collection name."""
        self._id = _id
        self.collection = "categories"

    def create(self, name):
        """Create a new category."""
        # make names unique if it does not already exist
        self.get_collection().create_index("name", unique=True)

        self.name = name
        return super().create()
