"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from utils.validator import is_valid_category


class TemplateSchema(BaseSchema):
    """Template Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    name = fields.Str(validate=is_valid_category)
    s3_url = fields.Str()
    is_approved = fields.Boolean(dump_default=False)
    is_go_template = fields.Boolean(dump_default=False)
