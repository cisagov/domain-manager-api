"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class ApplicationSchema(Schema):
    """Application Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
    requester_name = fields.Str(required=True)
    requested_date = fields.DateTime(required=True)
