"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas import application_schema


class History(Schema):
    """Application History Schema."""

    application = fields.Nested(application_schema.ApplicationSchema)
    launch_date = fields.DateTime()


class IsCategorySubmitted(Schema):
    """Submitted Categories Schema."""

    _id = fields.Str()
    name = fields.Str()
    is_categorized = fields.Boolean()


class Profile(Schema):
    """Template context data."""

    name = fields.Str()
    domain = fields.Str()
    description = fields.Str()
    email = fields.Str()
    phone = fields.Str()


class Redirect(Schema):
    """Schema for Redirects."""

    subdomain = fields.Str()
    redirect_url = fields.Str()


class WebsiteSchema(Schema):
    """Website Schema."""

    _id = fields.Str()
    name = fields.Str()
    description = fields.Str()
    category = fields.Str()
    s3_url = fields.Str()
    ip_address = fields.Str()
    application = fields.Nested(application_schema.ApplicationSchema)
    is_active = fields.Boolean()
    is_category_submitted = fields.List(fields.Nested(IsCategorySubmitted))
    is_email_active = fields.Boolean()
    launch_date = fields.DateTime()
    profile = fields.Dict()
    history = fields.List(fields.Nested(History))
    cloudfront = fields.Dict()
    acm = fields.Dict()
    route53 = fields.Dict()
    redirects = fields.List(fields.Nested(Redirect))
