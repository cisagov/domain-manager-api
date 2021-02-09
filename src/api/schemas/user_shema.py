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
    Attributes = fields.List(fields.Dict())
    Enabled = fields.Boolean()
    # Someone better with Python Datetimes should help here,
    # Im going crazy getting it to accept this
    # UserCreateDate = fields.DateTime()
    # UserLastModifiedDate = fields.DateTime()
    UserStatus = fields.Str()
    Username = fields.Str(validate=is_valid_category)
    Groups = fields.List(fields.Dict())
    History = fields.List(fields.Dict())
    HashedAPI = fields.Str()
    HasAPIKey = fields.Boolean()
