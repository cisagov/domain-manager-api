"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class ProxySchema(Schema):
    """Proxy Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
    script = fields.Str(required=True)
    created_by = fields.Str(required=True)
    created_date = fields.DateTime(required=True)
