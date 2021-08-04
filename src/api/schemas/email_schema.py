"""Email Schema."""
# Third-Party Libraries
from marshmallow import fields

# cisagov Libraries
from api.schemas.base_schema import BaseSchema


class EmailSchema(BaseSchema):
    """EmailSchema."""

    domain_id = fields.Str()
    timestamp = fields.Str()
    from_address = fields.Str()
    to_address = fields.Str()
    subject = fields.Str()
    message = fields.Str()
