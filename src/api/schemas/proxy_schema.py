"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class CategorySchema(Schema):
    """Category Schema."""

    category = fields.Str()


class ProxySchema(Schema):
    """Proxy Schema."""

    _id = fields.Str()
    name = fields.Str()
    url = fields.Str()
    script = fields.Str()
    categories = fields.List(fields.Nested(CategorySchema))
    created_by = fields.Str()
    created = fields.DateTime()
    updated = fields.DateTime()
