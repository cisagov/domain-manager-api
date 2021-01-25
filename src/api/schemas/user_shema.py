"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields

# cisagov Libraries
from utils.validator import is_valid_category


class UserSchema(Schema):
    """User Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    _id = fields.Str()
    name = fields.Str(validate=is_valid_category)
    is_activated = fields.Boolean()
    created = fields.DateTime()
    updated = fields.DateTime()
