"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class TemplateSchema(Schema):
    """Template Schema."""

    _id = fields.Str()
    name = fields.Str()
    s3_url = fields.Str()
    created = fields.DateTime()
    updated = fields.DateTime()
