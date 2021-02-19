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
    username = fields.Str(required=True, allow_none=True)
    is_admin = fields.Bool()
    status_code = fields.Number(required=True)
    path = fields.Str(required=True)
    method = fields.Str(required=True)
    args = fields.Dict()
    json = fields.Dict(allow_none=True)
    created = DateTimeField()
    error = fields.Str()
