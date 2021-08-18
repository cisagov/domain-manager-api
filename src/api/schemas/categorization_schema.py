"""CategorizationSchema."""
# Third-Party Libraries
from marshmallow import fields, validate

# cisagov Libraries
from api.schemas.base_schema import BaseSchema
from utils.categorization import CATEGORIES


class CategorizationSchema(BaseSchema):
    """DomainSchema."""

    domain_id = fields.Str()
    proxy = fields.Str()
    status = fields.Str(
        validate=validate.OneOf(["new", "submitted", "verified", "rejected"])
    )
    category = fields.Str(
        validate=validate.OneOf([category for category in CATEGORIES])
    )
    categorize_url = fields.Str(allow_none=True)
    check_url = fields.Str(allow_none=True)
