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

    application_name = fields.Str(required=False)
    args = fields.Dict()
    domain_name = fields.Str(required=False)
    error = fields.Str()
    is_admin = fields.Bool()
    method = fields.Str()
    json = fields.Field(allow_none=True)
    path = fields.Str()
    status_code = fields.Number()
    template_name = fields.Str(required=False)
    username = fields.Str()
