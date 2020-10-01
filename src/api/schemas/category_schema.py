"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class CategorySchema(Schema):
    """Category Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
