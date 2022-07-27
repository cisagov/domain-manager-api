"""Log Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class LogSchema(BaseSchema):
    """LogSchema."""

    class Meta:
        """Meta attributes for class."""

        unkown = EXCLUDE

    username = fields.Str()
    is_admin = fields.Bool()
    status_code = fields.Number()
    path = fields.Str()
    method = fields.Str()
    args = fields.Dict()
    json = fields.Field(allow_none=True)
    error = fields.Str()
    application_name = fields.Str(required=False)
    domain_name = fields.Str(required=False)
    template_name = fields.Str(required=False)
