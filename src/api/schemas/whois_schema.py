"""Whois Schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class WhoisSchema(BaseSchema):
    """Whois Schema."""

    domain_id = fields.Str()
    registrar = fields.Str()
    expiration_date = fields.DateTime()
    raw_data = fields.Dict()
