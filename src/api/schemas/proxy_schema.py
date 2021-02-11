"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields


class ProxySchema(Schema):
    """Proxy Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    _id = fields.Str()
    name = fields.Str()
    url = fields.Str()
    categories = fields.List(fields.Str())
