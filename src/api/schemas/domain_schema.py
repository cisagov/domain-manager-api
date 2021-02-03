"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields, validate, validates_schema

# cisagov Libraries
from api.schemas import application_schema
from utils.validator import (
    is_valid_category,
    is_valid_domain,
    is_valid_ipv4,
    validate_data,
)


class History(Schema):
    """Application History Schema."""

    application = fields.Nested(application_schema.ApplicationSchema)
    launch_date = fields.DateTime()


class IsCategorySubmitted(Schema):
    """Submitted Categories Schema."""

    _id = fields.Str()
    name = fields.Str()
    is_categorized = fields.Boolean()
    category = fields.Str()


class Profile(Schema):
    """Template context data."""

    name = fields.Str()
    domain = fields.Str()
    description = fields.Str()
    email = fields.Str()
    phone = fields.Str()


class Record(Schema):
    """Schema for Redirects."""

    class A(Schema):
        """Schema for an A Record."""

        value = fields.Str(required=True, validate=is_valid_ipv4)

    class CNAME(Schema):
        """Schema for CNAME record."""

        value = fields.Str(required=True, validate=is_valid_domain)

    class REDIRECT(Schema):
        """Schema for Redirect record."""

        value = fields.Str(required=True, validate=is_valid_domain)

    class MAILGUN(Schema):
        """Schema for Mailgun."""

        value = fields.Str(required=True)

    record_id = fields.Str()
    record_type = fields.Str(
        required=True, validate=validate.OneOf(["A", "CNAME", "MAILGUN", "REDIRECT"])
    )
    name = fields.Str(required=True, validate=is_valid_domain)
    config = fields.Dict(required=True)

    @validates_schema
    def validate_value(self, data, **kwargs):
        """Validate Schema."""
        types = {
            "A": self.A,
            "CNAME": self.CNAME,
            "REDIRECT": self.REDIRECT,
            "MAILGUN": self.MAILGUN,
        }
        validate_data(data["config"], types.get(data["record_type"].upper()))


class DomainSchema(Schema):
    """DomainSchema."""

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
    is_category_queued = fields.Boolean()
    is_category_submitted = fields.List(fields.Nested(IsCategorySubmitted))
    is_email_active = fields.Boolean()
    launch_date = fields.DateTime()
    profile = fields.Dict()
    history = fields.List(fields.Nested(History))
    cloudfront = fields.Dict()
    acm = fields.Dict()
    route53 = fields.Dict()
    records = fields.List(fields.Nested(Record))
