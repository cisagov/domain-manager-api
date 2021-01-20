"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields


class ApplicationSchema(Schema):
    """Application Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    _id = fields.Str()
    name = fields.Str()
    requester_name = fields.Str()
    contact_name = fields.Str()
    contact_email = fields.Email()
    contact_phone = fields.Str()
    created = fields.DateTime()
    updated = fields.DateTime()
