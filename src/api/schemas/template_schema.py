"""API Schema."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from marshmallow import Schema, fields


class TemplateSchema(Schema):
    """Template Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
    s3_url = fields.Str(required=True)
    created = fields.DateTime(required=True, default=datetime.now())
