"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField
from utils.validator import is_valid_category


class UserSchema(BaseSchema):
    """User Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    Attributes = fields.List(fields.Dict())
    Email = fields.Email()
    Enabled = fields.Boolean()
    UserCreateDate = DateTimeField(allow_none=True)
    UserLastModifiedDate = DateTimeField()
    UserStatus = fields.Str()
    Username = fields.Str(validate=is_valid_category)
    Groups = fields.List(fields.Dict())
    HashedAPI = fields.Str()
    HasAPIKey = fields.Boolean()
