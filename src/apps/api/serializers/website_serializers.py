"""API Serializers."""
# Third-Party Libraries
from marshmallow import Schema, fields


class WebsiteSerializer(Schema):
    """Website Serializer."""

    name = fields.Str(required=True)
    url = fields.Str(required=True)
