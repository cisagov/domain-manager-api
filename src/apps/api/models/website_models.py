"""API models."""
# Third-Party Libraries
from apps.database.repository.models import Model
from apps.database.repository.types import DateTimeType, StringType, UUIDType


class WebsiteModel(Model):
    """Website model."""

    website_uuid = UUIDType()
    name = StringType(required=True)
    url = StringType(required=True)
    created_by = StringType(required=True)
    last_updated = DateTimeType()


def validate_website(data_object):
    """This validates a Domain model."""
    return WebsiteModel(data_object).validate()
