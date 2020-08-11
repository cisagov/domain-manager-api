"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class WebsiteSchema(Schema):
    """Website Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
