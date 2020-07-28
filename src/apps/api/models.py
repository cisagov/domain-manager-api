from apps.database.repository.models import Model
from apps.database.repository.types import (
    DateTimeType,
    StringType,
    UUIDType,
)


class DomainModel(Model):
    domain_uuid = UUIDType()
    name = StringType(required=True)
    url = StringType(required=True)
    created_by = StringType(required=True)
    last_updated = DateTimeType()


def validate_domain(data_object):
    """
    This validates a Domain model.
    """
    return DomainModel(data_object).validate()
