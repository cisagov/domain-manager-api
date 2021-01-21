"""API Schema."""
# Third-Party Libraries
from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    validate,
    validates_schema,
)
import validators

# cisagov Libraries
from api.schemas import application_schema
from utils.validator import is_valid_category, is_valid_domain


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


class Record(Schema):
    """Schema for Redirects."""

    record_type = fields.Str(
        required=True, validate=validate.OneOf(["A", "CNAME", "MAILGUN", "REDIRECT"])
    )
    record_name = fields.Str(required=True, validate=is_valid_domain)
    record_value = fields.Str(required=True)

    @validates_schema
    def validate_value(self, data, **kwargs):
        """Validate Schema."""
        if data["record_type"] == "A":
            if not validators.ipv4(data["record_value"]):
                raise ValidationError("record_value must be an ipv4 address.")
        if data["record_type"] == "CNAME":
            if not validators.domain(data["record_value"]):
                raise ValidationError("record_value must be a domain.")


class WebsiteSchema(Schema):
    """Website Schema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

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
    records = fields.List(fields.Nested(Record))
