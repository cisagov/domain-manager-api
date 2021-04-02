"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields

# cisagov Libraries
from api.schemas.fields import DateTimeField
from utils.validator import is_valid_category


class TemplateSchema(Schema):
    """Template Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    _id = fields.Str()
    name = fields.Str(validate=is_valid_category)
    s3_url = fields.Str()
    is_approved = fields.Boolean(default=False)
    created = DateTimeField()
    updated = DateTimeField()
    created_by = fields.Str()
