"""API Schema."""
# Third-Party Libraries
from marshmallow import Schema, fields


class DomainSchema(Schema):
    """Domain Schema."""

    _id = fields.Str(required=True)
    ID = fields.Str(required=True)
    Name = fields.Str(required=True)
    Created = fields.Str(required=True)
    Expires = fields.Str(required=True)
    IsExpired = fields.Str(required=True)
    IsLocked = fields.Str(required=True)
    AutoRenew = fields.Str(required=True)
    IsPremium = fields.Str(required=True)
    IsOurDNS = fields.Str(required=True)
