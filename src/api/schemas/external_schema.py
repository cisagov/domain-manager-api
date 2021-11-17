"""API Schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField
from utils import validator


class ExternalSchema(BaseSchema):
    """External Domains Schema."""

    name = fields.Str(validate=validator.is_valid_domain)
    rejected_msg = fields.Str(allow_none=True)
    burned_date = DateTimeField()
    proxy_email = fields.Str(valid=validator.is_valid_email)
