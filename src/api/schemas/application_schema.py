"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class ApplicationSchema(BaseSchema):
    """Application Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    name = fields.Str()
    contact_name = fields.Str()
    contact_email = fields.Email()
    contact_phone = fields.Str()
