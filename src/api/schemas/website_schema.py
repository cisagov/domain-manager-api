"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas import application_schema, website_schema


class History(Schema):
    """Application History Schema."""

    application = fields.Nested(application_schema.ApplicationSchema)
    launch_date = fields.DateTime(required=False)


class IsCategorySubmitted(Schema):
    """Submitted Categories Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
    is_categorized = fields.Boolean(required=True)


class Profile(Schema):
    """Template context data."""

    name = fields.Str(required=True)
    domain = fields.Str(required=True)
    description = fields.Str(required=False)
    email = fields.Str(required=True)
    phone = fields.Str(required=True)


class WebsiteSchema(Schema):
    """Website Schema."""

    _id = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=False)
    ip_address = fields.Str(required=False)
    application = fields.Nested(application_schema.ApplicationSchema)
    is_active = fields.Boolean(required=True)
    is_category_submitted = fields.List(
        fields.Nested(IsCategorySubmitted, required=False)
    )
    is_email_active = fields.Boolean(required=True)
    launch_date = fields.DateTime(required=False)
    history = fields.List(fields.Nested(History, required=False))
