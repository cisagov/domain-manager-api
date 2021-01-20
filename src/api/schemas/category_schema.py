"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields


class CategorySchema(Schema):
    """Category Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    _id = fields.Str()
    name = fields.Str()
    proxies = fields.List(fields.Dict())
