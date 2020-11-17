"""API Schema."""
# Third-Party Libraries
from api.schemas import application_schema, website_schema
from marshmallow import Schema, fields


class IsCategorySubmitted(Schema):
    """Submitted categories Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
    is_categorized = fields.Boolean(required=True)


class ActiveSiteSchema(Schema):
    """Application Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=False)
    website = fields.Nested(website_schema.WebsiteSchema, required=False)
    ip_address = fields.Str(required=False)
    application = fields.Nested(application_schema.ApplicationSchema)
    is_submitted = fields.List(fields.Nested(IsCategorySubmitted, required=False))
    is_email_active = fields.Boolean(required=True)
    launch_date = fields.DateTime(required=True)
