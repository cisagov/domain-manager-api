from marshmallow import Schema, fields


class DomainSerializer(Schema):
    """
    Domain Models
    """

    name = fields.Str(required=True)
    url = fields.Str(required=True)
    created_by = fields.Str(required=True)
    last_updated = fields.DateTime()
