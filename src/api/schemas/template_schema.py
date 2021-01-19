"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from utils.validator import is_valid_category


class TemplateSchema(Schema):
    """Template Schema."""

    _id = fields.Str()
    name = fields.Str(validate=is_valid_category)
    preview_url = fields.Str()
    s3_url = fields.Str()
    created = fields.DateTime()
    updated = fields.DateTime()
