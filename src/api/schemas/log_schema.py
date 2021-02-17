"""Log Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields


class LogSchema(Schema):
    """LogSchema."""

    class Meta:
        """Meta attributes for class."""

        unkown = EXCLUDE

    _id = fields.Str()
    username = fields.Str(required=True)
    is_admin = fields.Bool()
    status_code = fields.Number(required=True)
    path = fields.Str(required=True)
    method = fields.Str(required=True)
    args = fields.Dict()
    json = fields.Dict()
    created = fields.DateTime()
    error = fields.Str()
