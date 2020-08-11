"""API Serializers."""
# Third-Party Libraries
from marshmallow import Schema, fields


class DomainSerializer(Schema):
    """Domain Serializers."""

    name = fields.Str(required=True)
    url = fields.Str(required=True)
    created_by = fields.Str(required=True)
    last_updated = fields.DateTime()
