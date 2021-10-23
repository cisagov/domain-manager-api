"""API Schema."""
# Third-Party Libraries
from marshmallow import EXCLUDE, Schema, fields, pre_load, validate, validates_schema

# cisagov Libraries
from api.schemas import application_schema
from api.schemas.base_schema import BaseSchema
from api.schemas.fields import DateTimeField
from utils import validator


class History(Schema):
    """Application History Schema."""

    application = fields.Nested(application_schema.ApplicationSchema)
    start_date = DateTimeField()
    end_date = DateTimeField()


class Profile(Schema):
    """Template context data."""

    name = fields.Str()
    city = fields.Str()
    domain = fields.Str()
    description = fields.Str()
    email = fields.Str()
    phone = fields.Str()
    state = fields.Str()


class Record(Schema):
    """Schema for Redirects."""

    class A(Schema):
        """Schema for an A Record."""

        value = fields.Str(required=True, validate=validator.is_valid_ipv4)

    class AAAA(Schema):
        """Schema for an AAAA Record."""

        value = fields.Str(required=True, validate=validator.is_valid_ipv6)

    class CNAME(Schema):
        """Schema for CNAME record."""

        value = fields.Str(required=True, validate=validator.is_valid_domain)

    class MX(Schema):
        """Schema for MX record."""

        value = fields.Str(required=True, validate=validator.is_valid_mx)

    class NS(Schema):
        """Schema for NS record."""

        value = fields.Str(required=True, validate=validator.is_valid_ns)

    class PTR(Schema):
        """Schema for PTR record."""

        value = fields.Str(required=True, validate=validator.is_valid_ipv4)

    class SRV(Schema):
        """Schema for SRV record."""

        value = fields.Str(required=True, validate=validator.is_valid_srv)

    class TXT(Schema):
        """Schema for TXT record."""

        value = fields.Str(required=True)

        @pre_load
        def wrap_value(self, in_data, **kwargs):
            """Wrap TXT values with quotes."""
            new_lines = []
            for line in in_data["value"].splitlines():
                if line and not line.startswith('"') and not line.endswith('"'):
                    new_lines.append(f'"{line}"')
                elif line:
                    new_lines.append(line)
            in_data["value"] = "\n".join(new_lines)
            return in_data

    class REDIRECT(Schema):
        """Schema for Redirect record."""

        value = fields.Str(required=True, validate=validator.is_valid_domain)
        protocol = fields.Str(
            missing="https",
            validate=validate.OneOf(["http", "https"]),
        )

    record_id = fields.Str()
    record_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "A",
                "AAAA",
                "CNAME",
                "MX",
                "PTR",
                "NS",
                "SRV",
                "TXT",
                "REDIRECT",
            ]
        ),
    )
    name = fields.Str(required=True, validate=validator.is_valid_domain)
    ttl = fields.Integer(default=30, missing=30)
    config = fields.Dict(required=True)

    @validates_schema
    def validate_value(self, data, **kwargs):
        """Validate Schema."""
        validated_data = validator.validate_data(
            data["config"], getattr(self, data["record_type"].upper())
        )
        data["config"] = validated_data
        return data


class DomainSchema(BaseSchema):
    """DomainSchema."""

    class Meta:
        """Meta atrributes for class."""

        unknown = EXCLUDE

    name = fields.Str(validate=validator.is_valid_domain)
    template_name = fields.Str(validate=validator.is_valid_category)
    s3_url = fields.Str()
    ip_address = fields.Str()
    application_id = fields.Str(allow_none=True)
    is_active = fields.Boolean()
    is_approved = fields.Boolean(default=False)
    is_available = fields.Boolean(default=True)
    is_launching = fields.Boolean(default=False)
    is_delaunching = fields.Boolean(default=False)
    is_generating_template = fields.Boolean(default=False)
    is_email_active = fields.Boolean()
    rejected_msg = fields.Str(allow_none=True)
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
