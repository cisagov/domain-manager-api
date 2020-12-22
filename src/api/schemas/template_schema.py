"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class TemplateSchema(Schema):
    """Template Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
