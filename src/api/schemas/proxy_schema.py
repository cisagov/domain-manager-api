"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields


class ProxySchema(Schema):
    """Proxy Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    name = fields.Str()
    url = fields.Str()
    categories = fields.List(fields.Str())
