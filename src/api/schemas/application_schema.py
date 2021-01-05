"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class ApplicationSchema(Schema):
    """Application Schema."""

    _id = fields.Str()
    name = fields.Str()
    requester_name = fields.Str()
    created = fields.DateTime()
    updated = fields.DateTime()
