"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, ValidationError, fields


class BytesField(fields.Field):
    """BytesField."""

    def _validate(self, value):
        """Validate data is bytes."""
        if not isinstance(value, bytes):
            raise ValidationError("Invalid input type.")

        if value is None or value == b"":
            raise ValidationError("Invalid value")


class ProxySchema(Schema):
    """Proxy Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    _id = fields.Str()
    name = fields.Str()
    url = fields.Str()
    script = BytesField()
    categories = fields.List(fields.Str())
    created_by = fields.Str()
    created = fields.DateTime()
    updated = fields.DateTime()
