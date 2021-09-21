"""Schema for settings collection."""
# Third-Party Libraries
from marshmallow import fields
from marshmallow.schema import Schema
from marshmallow.utils import EXCLUDE

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class SettingsSchema(BaseSchema):
    """
    SettingsSchema.

    This is the schema for the method that settings are stored in the database.
    """

    key = fields.Str()
    value = fields.Str(allow_none=True)


class SettingsPostSchema(Schema):
    """
    SettingsPostSchema.

    This is the way new settings are posted and validators to go along with it.
    """

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    SES_FORWARD_EMAIL = fields.Email(allow_none=True)
    USER_NOTIFICATION_EMAIL = fields.Email(allow_none=True)
    CATEGORIZATION_EMAIL = fields.Email(allow_none=True)
