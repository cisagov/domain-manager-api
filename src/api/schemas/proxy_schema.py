"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class CategorySchema(Schema):
    """Category Schema."""

    category = fields.Str(required=True)


class ProxySchema(Schema):
    """Proxy Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
    script = fields.Str(required=True)
    categories = fields.List(fields.Nested(CategorySchema), required=True)
    created_by = fields.Str(required=True)
    created = fields.DateTime(required=True)
