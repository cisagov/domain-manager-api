"""Website document."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from utils.db.base import Document
from utils.db.datatypes import BooleanType, DictType, StringType, DatetimeType


class Website(Document):
    """Website document model."""

    name: StringType
    s3_url: StringType
    is_active: BooleanType
    is_category_submitted: BooleanType
    is_categorized: BooleanType
    is_email_active: BooleanType
    launch_date: DatetimeType
    application: DictType
    history: DictType
    cloudfront: DictType
    acm: DictType
    route53: DictType

    def __init__(self, _id=None):
        """Initialize collection and indices."""
        self._id = _id
        self.collection = "websites"
        self.indexes = ["name"]

    def create(self, name):
        """Create a new website."""
        self.launch_date = datetime.now()
        return super().create()
