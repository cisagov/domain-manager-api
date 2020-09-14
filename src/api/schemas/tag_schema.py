"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class TagSchema(Schema):
    """Tag Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
