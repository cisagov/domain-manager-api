"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class DomainConfigSchema(Schema):
    """Route53 Config Schema."""

    Comment = fields.Str(required=True)
    PrivateZone = fields.Bool(required=True)


class DomainSchema(Schema):
    """Domain Schema."""

    _id = fields.Str(required=True)
    Id = fields.Str(required=True)
    Name = fields.Str(required=True)
    CallerReference = fields.Str(required=True)
    Config = fields.Nested(DomainConfigSchema)
    ResourceRecordSetCount = fields.Int(required=True)
