"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields

# cisagov Libraries
from api.schemas.fields import DateTimeField
from utils.validator import is_valid_category


class UserSchema(Schema):
    """User Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    _id = fields.Str()
    Attributes = fields.List(fields.Dict())
    Enabled = fields.Boolean()
    UserCreateDate = DateTimeField()
    UserLastModifiedDate = DateTimeField()
    UserStatus = fields.Str()
    Username = fields.Str(validate=is_valid_category)
    Groups = fields.List(fields.Dict())
    HashedAPI = fields.Str()
    HasAPIKey = fields.Boolean()
