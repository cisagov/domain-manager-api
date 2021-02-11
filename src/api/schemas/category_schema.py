"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields


class CategorySchema(Schema):
    """Category Schema."""

    class Meta:
        """Meta attributes for class."""

        unknown = EXCLUDE

    name = fields.Str()
    proxies = fields.List(fields.Dict())
