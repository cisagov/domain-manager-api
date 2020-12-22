"""Website document."""
# Standard Python Libraries
from datetime import datetime

# cisagov Libraries
from utils.db.base import Document
from utils.db.datatypes import BooleanType, DatetimeType, DictType, ListType, StringType


class Website(Document):
    """Website document model."""

    name: StringType
    description: StringType
    category: StringType
    s3_url: StringType
    ip_address: StringType
    application: ListType
    is_active: BooleanType
    is_category_submitted: ListType
    is_email_active: BooleanType
    launch_date: DatetimeType
    profile: DictType
    history: ListType
    cloudfront: DictType
    acm: DictType
    route53: DictType

    def __init__(self, _id=None):
        """Initialize collection and indices."""
        self._id = _id
        self.collection = "websites"
        self.indexes = ["name"]
