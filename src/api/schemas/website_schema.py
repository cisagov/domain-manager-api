"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields

# cisagov Libraries
from api.schemas import application_schema
from utils.validator import is_valid_category, is_valid_domain, validate


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

    subdomain = fields.Str(validate=validate.ContainsNoneOf([" "]))
    redirect_url = fields.Str(validate=is_valid_domain)


class WebsiteSchema(Schema):
    """Website Schema."""

    _id = fields.Str()
    name = fields.Str(validate=is_valid_domain)
    description = fields.Str()
    category = fields.Str(validate=is_valid_category)
    s3_url = fields.Str()
    ip_address = fields.Str()
    application_id = fields.Str()
    is_active = fields.Boolean()
    is_available = fields.Boolean()
    is_launching = fields.Boolean()
    is_delaunching = fields.Boolean()
    is_generating_template = fields.Boolean()
    is_category_submitted = fields.List(fields.Nested(IsCategorySubmitted))
    is_email_active = fields.Boolean()
    launch_date = fields.DateTime()
    profile = fields.Dict()
    history = fields.List(fields.Nested(History))
    cloudfront = fields.Dict()
    acm = fields.Dict()
    route53 = fields.Dict()
    redirects = fields.List(fields.Nested(Redirect))
