"""Log Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields

# cisagov Libraries
from api.schemas.fields import DateTimeField


class LogSchema(Schema):
    """LogSchema."""

    class Meta:
        """Meta attributes for class."""

        unkown = EXCLUDE

    _id = fields.Str()
    username = fields.Str()
    is_admin = fields.Bool()
    status_code = fields.Number()
    path = fields.Str()
    method = fields.Str()
    args = fields.Dict()
    json = fields.Field(allow_none=True)
    created = DateTimeField()
    error = fields.Str()
