"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields, pre_load, validate, validates_schema

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

    name = fields.Str()
    is_categorized = fields.Boolean()
    category = fields.Str(allow_none=True)


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
        protocol = fields.Str(
            missing="https", validate=validate.OneOf(["http", "https"])
        )

    class MAILGUN(Schema):
        """Schema for Mailgun."""

        key = fields.Str(required=True)
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
        validated_data = validate_data(
            data["config"], types.get(data["record_type"].upper())
        )
        data["config"] = validated_data
        return data


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
    is_available = fields.Boolean(default=True)
    is_launching = fields.Boolean(default=False)
    is_delaunching = fields.Boolean(default=False)
    is_generating_template = fields.Boolean(default=False)
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

    @pre_load
    def clean_data(self, in_data, **kwargs):
        """Clean domain data before loading to database."""
        if in_data.get("name"):
            in_data["name"] = in_data["name"].lower().strip()
        return in_data
