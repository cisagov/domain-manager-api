"""API Schema."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from marshmallow import Schema, fields


class ApplicationSchema(Schema):
    """Application Schema."""

    _id = fields.Str()
    name = fields.Str()
    requester_name = fields.Str()
    created = fields.DateTime(default=datetime.now())
