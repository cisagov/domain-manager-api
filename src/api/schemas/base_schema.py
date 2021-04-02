"""BaseSchema."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas.fields import DateTimeField


class BaseSchema(Schema):
    """
    BaseSchema.

    The base schema for all collections.
    """

    _id = fields.Str()
    created = DateTimeField(allow_none=True)
    created_by = fields.Str()
    updated = DateTimeField(allow_none=True)
    updated_by = fields.Str()
